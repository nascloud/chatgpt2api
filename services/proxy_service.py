"""Upstream proxy configuration for requests against chatgpt.com.

Only chatgpt.com traffic goes through this proxy. Internal services like
sub2api / CPA pools always call their own base_url directly.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from threading import Lock
from urllib.parse import urlparse

from curl_cffi.requests import Session

from services.config import DATA_DIR


PROXY_CONFIG_FILE = DATA_DIR / "proxy_config.json"


def _clean(value: object) -> str:
    return str(value or "").strip()


def _is_valid_proxy_url(url: str) -> bool:
    if not url:
        return False
    try:
        parsed = urlparse(url)
    except Exception:
        return False
    if parsed.scheme not in {"http", "https", "socks4", "socks5", "socks5h"}:
        return False
    return bool(parsed.hostname)


class ProxyConfig:
    def __init__(self, store_file: Path):
        self._store_file = store_file
        self._lock = Lock()
        self._state = self._load()

    def _default_state(self) -> dict:
        env_url = _clean(os.getenv("CHATGPT2API_PROXY"))
        if env_url and _is_valid_proxy_url(env_url):
            return {"enabled": True, "url": env_url}
        return {"enabled": False, "url": ""}

    def _load(self) -> dict:
        if not self._store_file.exists():
            return self._default_state()
        try:
            raw = json.loads(self._store_file.read_text(encoding="utf-8"))
        except Exception:
            return self._default_state()
        if not isinstance(raw, dict):
            return self._default_state()
        return {
            "enabled": bool(raw.get("enabled")),
            "url": _clean(raw.get("url")),
        }

    def _save(self) -> None:
        self._store_file.parent.mkdir(parents=True, exist_ok=True)
        self._store_file.write_text(
            json.dumps(self._state, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def get(self) -> dict:
        with self._lock:
            return dict(self._state)

    def get_public(self) -> dict:
        state = self.get()
        return {
            "enabled": bool(state.get("enabled")),
            "url": _clean(state.get("url")),
        }

    def update(self, *, enabled: bool | None, url: str | None) -> dict:
        with self._lock:
            next_state = dict(self._state)
            if enabled is not None:
                next_state["enabled"] = bool(enabled)
            if url is not None:
                new_url = _clean(url)
                if new_url and not _is_valid_proxy_url(new_url):
                    raise ValueError("invalid proxy url")
                next_state["url"] = new_url
            if next_state.get("enabled") and not next_state.get("url"):
                raise ValueError("proxy url is required when enabled")
            self._state = next_state
            self._save()
            return dict(self._state)

    def get_proxies(self) -> dict[str, str] | None:
        """Return a dict suitable for curl_cffi's `proxies=` kwarg, or None."""
        state = self.get()
        if not state.get("enabled"):
            return None
        url = _clean(state.get("url"))
        if not url:
            return None
        return {"http": url, "https": url}


proxy_config = ProxyConfig(PROXY_CONFIG_FILE)


def get_chatgpt_proxies() -> dict[str, str] | None:
    """Return the proxies dict for chatgpt.com requests, or None if proxy is disabled."""
    return proxy_config.get_proxies()


def apply_proxy_to_session(session: Session) -> None:
    """Attach the current upstream proxy to a curl_cffi Session, if configured.

    Prefer passing `proxies=get_chatgpt_proxies()` directly to Session(...) instead —
    some curl_cffi versions only honor proxies set at construction time. This helper
    is kept for cases where the Session is created elsewhere.
    """
    proxies = get_chatgpt_proxies()
    if proxies:
        session.proxies = dict(proxies)


def test_proxy(url: str, *, timeout: float = 15.0) -> dict:
    """Probe chatgpt.com through the given proxy URL. Returns {ok, status, latency_ms, error}."""
    candidate = _clean(url)
    if not candidate:
        return {"ok": False, "status": 0, "latency_ms": 0, "error": "proxy url is required"}
    if not _is_valid_proxy_url(candidate):
        return {"ok": False, "status": 0, "latency_ms": 0, "error": "invalid proxy url"}

    session = Session(impersonate="edge101", verify=True)
    session.proxies.update({"http": candidate, "https": candidate})
    started = time.perf_counter()
    try:
        response = session.get(
            "https://chatgpt.com/api/auth/csrf",
            headers={"user-agent": "Mozilla/5.0 (chatgpt2api proxy test)"},
            timeout=timeout,
        )
        latency_ms = int((time.perf_counter() - started) * 1000)
        return {
            "ok": response.status_code < 500,
            "status": int(response.status_code),
            "latency_ms": latency_ms,
            "error": None if response.status_code < 500 else f"HTTP {response.status_code}",
        }
    except Exception as exc:
        latency_ms = int((time.perf_counter() - started) * 1000)
        return {
            "ok": False,
            "status": 0,
            "latency_ms": latency_ms,
            "error": str(exc) or exc.__class__.__name__,
        }
    finally:
        session.close()
