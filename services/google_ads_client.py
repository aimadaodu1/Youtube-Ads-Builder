"""Google Ads API client helpers."""
from __future__ import annotations

from typing import Dict, List, Optional

from .config_manager import normalize_customer_id

try:
    from google.ads.googleads.client import GoogleAdsClient
except Exception:  # Lets Streamlit load before dependencies are installed.
    GoogleAdsClient = None  # type: ignore


def load_client(yaml_path: str):
    if GoogleAdsClient is None:
        raise RuntimeError("google-ads is not installed. Run: pip install -r requirements.txt")
    return GoogleAdsClient.load_from_storage(yaml_path)


def test_connection(yaml_path: str, customer_id: Optional[str] = None) -> Dict:
    client = load_client(yaml_path)
    customer_service = client.get_service("CustomerService")
    accessible = customer_service.list_accessible_customers()
    resource_names: List[str] = list(accessible.resource_names)

    result: Dict = {
        "ok": True,
        "accessible_customers": resource_names,
        "campaign_count": None,
        "message": "Connection succeeded.",
    }

    cid = normalize_customer_id(customer_id or "")
    if cid:
        ga_service = client.get_service("GoogleAdsService")
        query = """
            SELECT campaign.id, campaign.name, campaign.status
            FROM campaign
            ORDER BY campaign.id
            LIMIT 10
        """
        count = 0
        for _row in ga_service.search(customer_id=cid, query=query):
            count += 1
        result["campaign_count"] = count
    return result


def format_google_ads_exception(ex: Exception) -> str:
    if hasattr(ex, "failure"):
        lines = []
        for error in ex.failure.errors:  # type: ignore[attr-defined]
            lines.append(getattr(error, "message", str(error)))
        return "\n".join(lines) or str(ex)
    return str(ex)
