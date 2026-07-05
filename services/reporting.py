"""Read/report on existing classic VIDEO campaigns."""
from __future__ import annotations

from typing import Dict, List

from .google_ads_client import load_client, normalize_customer_id


def list_existing_video_campaigns(yaml_path: str, customer_id: str, limit: int = 20) -> List[Dict]:
    client = load_client(yaml_path)
    cid = normalize_customer_id(customer_id)
    if not cid:
        raise ValueError("Customer ID is required.")
    ga_service = client.get_service("GoogleAdsService")
    query = f"""
        SELECT
          campaign.id,
          campaign.name,
          campaign.status,
          campaign.advertising_channel_type,
          metrics.impressions,
          metrics.views,
          metrics.cost_micros
        FROM campaign
        WHERE campaign.advertising_channel_type = 'VIDEO'
        ORDER BY campaign.id DESC
        LIMIT {int(limit)}
    """
    rows = []
    for row in ga_service.search(customer_id=cid, query=query):
        rows.append({
            "id": row.campaign.id,
            "name": row.campaign.name,
            "status": row.campaign.status.name,
            "impressions": row.metrics.impressions,
            "views": row.metrics.views,
            "cost_usd": round(row.metrics.cost_micros / 1_000_000, 2),
        })
    return rows
