"""Export helpers for campaign briefs."""
from __future__ import annotations

import csv
import json
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Dict, Tuple

EXPORT_DIR = Path("exports")


def _safe_name(name: str) -> str:
    clean = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in name)
    return clean.strip("_")[:80] or "campaign"


def brief_to_json_bytes(brief: Dict) -> bytes:
    return json.dumps(brief, indent=2, ensure_ascii=False).encode("utf-8")


def brief_to_csv_bytes(brief: Dict) -> bytes:
    out = StringIO()
    writer = csv.DictWriter(out, fieldnames=["field", "value"])
    writer.writeheader()
    for key, value in brief.items():
        if isinstance(value, list):
            value = " | ".join(map(str, value))
        elif isinstance(value, dict):
            value = json.dumps(value, ensure_ascii=False)
        writer.writerow({"field": key, "value": value})
    return out.getvalue().encode("utf-8")


def export_brief(brief: Dict, campaign_name: str) -> Tuple[str, str]:
    EXPORT_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = f"{stamp}_{_safe_name(campaign_name)}"
    json_path = EXPORT_DIR / f"{base}.json"
    csv_path = EXPORT_DIR / f"{base}.csv"
    json_path.write_bytes(brief_to_json_bytes(brief))
    csv_path.write_bytes(brief_to_csv_bytes(brief))
    return str(json_path), str(csv_path)
