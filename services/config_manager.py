"""Local setup/configuration helpers for YouTube Ads Builder.

The app writes Google Ads API credentials to a local YAML file so users do not
have to manually edit google-ads.yaml. Keep the config folder private.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT_DIR / "config"
APP_CONFIG_PATH = CONFIG_DIR / "app_config.json"
GOOGLE_ADS_YAML_PATH = CONFIG_DIR / "google-ads.yaml"


def ensure_config_dir() -> Path:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_DIR


def normalize_customer_id(customer_id: str | int | None) -> str:
    return "".join(ch for ch in str(customer_id or "") if ch.isdigit())


def load_app_config() -> Dict[str, Any]:
    ensure_config_dir()
    if not APP_CONFIG_PATH.exists():
        return {
            "yaml_path": str(GOOGLE_ADS_YAML_PATH),
            "customer_id": "",
            "login_customer_id": "",
        }
    try:
        with APP_CONFIG_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("yaml_path", str(GOOGLE_ADS_YAML_PATH))
        data.setdefault("customer_id", "")
        data.setdefault("login_customer_id", "")
        return data
    except Exception:
        return {
            "yaml_path": str(GOOGLE_ADS_YAML_PATH),
            "customer_id": "",
            "login_customer_id": "",
        }


def save_app_config(customer_id: str, yaml_path: str | None = None, login_customer_id: str | None = None) -> Dict[str, Any]:
    ensure_config_dir()
    config = load_app_config()
    config["customer_id"] = normalize_customer_id(customer_id)
    config["yaml_path"] = yaml_path or str(GOOGLE_ADS_YAML_PATH)
    config["login_customer_id"] = normalize_customer_id(login_customer_id or config.get("login_customer_id", ""))
    with APP_CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    return config


def _yaml_quote(value: str) -> str:
    # Avoid PyYAML as a hard requirement for this small config file.
    escaped = str(value or "").replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def save_google_ads_yaml(
    developer_token: str,
    client_id: str,
    client_secret: str,
    refresh_token: str,
    login_customer_id: str | None = None,
    path: str | Path | None = None,
) -> Path:
    """Write a google-ads.yaml file compatible with GoogleAdsClient.load_from_storage."""
    ensure_config_dir()
    output_path = Path(path) if path else GOOGLE_ADS_YAML_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        f"developer_token: {_yaml_quote(developer_token.strip())}",
        f"client_id: {_yaml_quote(client_id.strip())}",
        f"client_secret: {_yaml_quote(client_secret.strip())}",
        f"refresh_token: {_yaml_quote(refresh_token.strip())}",
        "use_proto_plus: true",
    ]
    login = normalize_customer_id(login_customer_id)
    if login:
        lines.append(f"login_customer_id: {_yaml_quote(login)}")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


def read_google_ads_yaml(path: str | Path | None = None) -> Dict[str, str]:
    """Small YAML reader for the simple key:value file this app writes."""
    target = Path(path) if path else GOOGLE_ADS_YAML_PATH
    if not target.exists():
        return {}
    data: Dict[str, str] = {}
    for raw in target.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip().strip('"').strip("'")
        data[key.strip()] = value
    return data


def has_google_ads_yaml(path: str | Path | None = None) -> bool:
    target = Path(path) if path else GOOGLE_ADS_YAML_PATH
    return target.exists()


def mask(value: str, visible: int = 4) -> str:
    value = str(value or "")
    if not value:
        return ""
    if len(value) <= visible:
        return "•" * len(value)
    return "•" * max(0, len(value) - visible) + value[-visible:]
