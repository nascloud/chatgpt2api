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
