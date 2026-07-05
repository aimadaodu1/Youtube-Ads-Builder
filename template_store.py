"""Very small local JSON template store."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

STORE_PATH = Path("data/templates.json")


def _load_all() -> List[Dict]:
    if not STORE_PATH.exists():
        return []
    try:
        return json.loads(STORE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def list_templates() -> List[Dict]:
    return sorted(_load_all(), key=lambda t: t.get("updated_at", ""), reverse=True)


def save_template(name: str, brief: Dict) -> Dict:
    STORE_PATH.parent.mkdir(exist_ok=True)
    templates = _load_all()
    now = datetime.now().isoformat(timespec="seconds")
    record = {"name": name.strip() or brief.get("campaign_name", "Untitled"), "updated_at": now, "brief": brief}
    templates = [t for t in templates if t.get("name") != record["name"]]
    templates.insert(0, record)
    STORE_PATH.write_text(json.dumps(templates, indent=2), encoding="utf-8")
    return record


def get_template(name: str) -> Optional[Dict]:
    for template in _load_all():
        if template.get("name") == name:
            return template
    return None


def delete_template(name: str) -> bool:
    templates = _load_all()
    new_templates = [t for t in templates if t.get("name") != name]
    STORE_PATH.write_text(json.dumps(new_templates, indent=2), encoding="utf-8")
    return len(new_templates) != len(templates)
