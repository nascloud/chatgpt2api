"""Global outbound proxy helpers for upstream ChatGPT and CPA requests."""

from __future__ import annotations

from services.config import config


class ProxySettingsStore:

    def build_session_kwargs(self, **session_kwargs) -> dict[str, object]:
        proxy = config.get_proxy_settings()
        if proxy:
            session_kwargs["proxy"] = proxy
        return session_kwargs


proxy_settings = ProxySettingsStore()


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
