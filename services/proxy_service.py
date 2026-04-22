"""Global outbound proxy settings for upstream ChatGPT and CPA requests."""

from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from urllib.parse import quote

from services.config import DATA_DIR


PROXY_SETTINGS_FILE = DATA_DIR / "proxy_settings.json"
ALLOWED_PROXY_SCHEMES = {"http", "https", "socks5", "socks5h"}


def _normalize_scheme(raw: object) -> str:
    value = str(raw or "http").strip().lower()
    return value if value in ALLOWED_PROXY_SCHEMES else "http"


def _normalize_port(raw: object) -> int | None:
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return None
    return value if 1 <= value <= 65535 else None


def _normalize_settings(raw: object) -> dict[str, object]:
    source = raw if isinstance(raw, dict) else {}
    return {
        "enabled": bool(source.get("enabled")),
        "scheme": _normalize_scheme(source.get("scheme")),
        "host": str(source.get("host") or "").strip(),
        "port": _normalize_port(source.get("port")),
        "username": str(source.get("username") or "").strip(),
        "password": str(source.get("password") or "").strip(),
    }


def _validate_settings(settings: dict[str, object]) -> None:
    host = str(settings.get("host") or "").strip()
    port = _normalize_port(settings.get("port"))
    username = str(settings.get("username") or "").strip()
    password = str(settings.get("password") or "").strip()
    has_custom_values = bool(host or port is not None or username or password)

    if host and "://" in host:
        raise ValueError("代理主机不要包含协议前缀")
    if has_custom_values:
        if not host:
            raise ValueError("代理主机不能为空")
        if port is None:
            raise ValueError("代理端口不能为空")
    if password and not username:
        raise ValueError("填写代理密码时必须同时填写用户名")


def _wrap_host(host: str) -> str:
    value = str(host or "").strip()
    if ":" in value and not value.startswith("[") and not value.endswith("]"):
        return f"[{value}]"
    return value


def _build_proxy_url(settings: dict[str, object]) -> str:
    if not bool(settings.get("enabled")):
        return ""

    host = str(settings.get("host") or "").strip()
    port = _normalize_port(settings.get("port"))
    if not host or port is None:
        return ""

    scheme = _normalize_scheme(settings.get("scheme"))
    username = str(settings.get("username") or "").strip()
    password = str(settings.get("password") or "").strip()

    auth = ""
    if username:
        auth = quote(username, safe="")
        if password:
            auth += f":{quote(password, safe='')}"
        auth += "@"

    return f"{scheme}://{auth}{_wrap_host(host)}:{port}"


class ProxySettingsStore:
    def __init__(self, store_file: Path):
        self._store_file = store_file
        self._lock = Lock()
        self._settings = self._load()

    def _load(self) -> dict[str, object]:
        if not self._store_file.exists():
            return _normalize_settings({})
        try:
            raw = json.loads(self._store_file.read_text(encoding="utf-8"))
        except Exception:
            return _normalize_settings({})
        normalized = _normalize_settings(raw)
        try:
            _validate_settings(normalized)
        except ValueError:
            return _normalize_settings({})
        return normalized

    def _save(self) -> None:
        self._store_file.parent.mkdir(parents=True, exist_ok=True)
        self._store_file.write_text(
            json.dumps(self._settings, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def _public_settings(settings: dict[str, object]) -> dict[str, object]:
        return {
            "enabled": bool(settings.get("enabled")),
            "scheme": _normalize_scheme(settings.get("scheme")),
            "host": str(settings.get("host") or "").strip(),
            "port": _normalize_port(settings.get("port")),
            "username": str(settings.get("username") or "").strip(),
            "has_password": bool(str(settings.get("password") or "").strip()),
        }

    def get_settings(self, *, include_secret: bool = False) -> dict[str, object]:
        with self._lock:
            settings = dict(self._settings)
        if include_secret:
            return settings
        return self._public_settings(settings)

    def update_settings(self, updates: dict[str, object]) -> dict[str, object]:
        allowed_updates = {
            key: value
            for key, value in updates.items()
            if key in {"enabled", "scheme", "host", "port", "username", "password"}
        }

        with self._lock:
            merged = {**self._settings, **allowed_updates}
            if "password" not in allowed_updates:
                merged["password"] = self._settings.get("password") or ""
            normalized = _normalize_settings(merged)
            _validate_settings(normalized)
            self._settings = normalized
            self._save()
            return self._public_settings(self._settings)

    def build_session_kwargs(self, **session_kwargs) -> dict[str, object]:
        with self._lock:
            proxy_url = _build_proxy_url(self._settings)
        if proxy_url:
            session_kwargs["proxy"] = proxy_url
        return session_kwargs


proxy_settings = ProxySettingsStore(PROXY_SETTINGS_FILE)
