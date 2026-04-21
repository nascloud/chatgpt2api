from __future__ import annotations
import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import cast

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
CONFIG_FILE = BASE_DIR / "config.json"
CONFIG_EXAMPLE_FILE = BASE_DIR / "config.example.json"


@dataclass(frozen=True)
class AppSettings:
    auth_key: str
    host: str
    port: int
    accounts_file: Path
    refresh_account_interval_minute: int


def _load_json_object(path: Path, *, name: str) -> dict[str, object]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return {}
    loaded = json.loads(text)
    if not isinstance(loaded, dict):
        raise ValueError(f"{name} must be a JSON object")
    return loaded


def _ensure_config_file() -> None:
    """本地开发时，如果没有 config.json 就从 example 复制一份"""
    if CONFIG_FILE.exists():
        return
    if not CONFIG_EXAMPLE_FILE.exists():
        return
    shutil.copyfile(CONFIG_EXAMPLE_FILE, CONFIG_FILE)
    print(f"✅ 已自动从 config.example.json 创建 {CONFIG_FILE}")


def _load_settings() -> AppSettings:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    _ensure_config_file()

    # 优先读取用户自己的 config.json（生产环境推荐）
    raw_config: dict[str, object] = {}
    if CONFIG_FILE.exists():
        raw_config.update(_load_json_object(CONFIG_FILE, name="config.json"))
    # 示例文件只作为参考，不再强制要求它里面有 auth-key
    elif CONFIG_EXAMPLE_FILE.exists():
        raw_config.update(_load_json_object(CONFIG_EXAMPLE_FILE, name="config.example.json"))

    # ==================== 关键修改部分 ====================
    # 1. 优先使用环境变量（Render / Docker / 任何 PaaS 都推荐这样）
    # 2. 再 fallback 到 config.json
    # 3. 错误提示更清晰，不再误导说 “config.example.json”
    auth_key = str(
        os.getenv("CHATGPT2API_AUTH_KEY")
        or raw_config.get("auth-key")
        or ""
    ).strip()

    if not auth_key:
        raise ValueError(
            "❌ auth-key 未设置！\n"
            "请按以下任意一种方式解决：\n"
            "1. 在 Render 的 Environment 变量中添加：\n"
            "   CHATGPT2API_AUTH_KEY = your_real_auth_key\n"
            "2. 或者在 config.json 中填写：\n"
            '   "auth-key": "your_real_auth_key"'
        )

    refresh_account_interval_minute = cast(
        int, raw_config.get("refresh_account_interval_minute", 5)
    )

    return AppSettings(
        auth_key=auth_key,
        host="0.0.0.0",
        port=8000,
        accounts_file=DATA_DIR / "accounts.json",
        refresh_account_interval_minute=refresh_account_interval_minute,
    )


config = _load_settings()
