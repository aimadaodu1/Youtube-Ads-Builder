"""Experimental paused Demand Gen campaign shell creation.

This intentionally creates only the campaign foundation because Demand Gen asset/ad
requirements can change and vary by account. Finish assets/audiences in Google Ads.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Dict

from .google_ads_client import load_client, normalize_customer_id


def _micros_from_dollars(dollars: float) -> int:
    return int(round(float(dollars) * 1_000_000))


def create_paused_demand_gen_shell(
    yaml_path: str,
    customer_id: str,
    campaign_name: str,
    daily_budget: float,
    target_cpa: float = 1.0,
    duration_days: int = 30,
) -> Dict:
    client = load_client(yaml_path)
    cid = normalize_customer_id(customer_id)
    if not cid:
        raise ValueError("Customer ID is required.")

    budget_service = client.get_service("CampaignBudgetService")
    budget_operation = client.get_type("CampaignBudgetOperation")
    budget = budget_operation.create
    budget.name = f"{campaign_name} Demand Gen Budget {date.today().isoformat()}"
    budget.amount_micros = _micros_from_dollars(daily_budget)
    budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
    try:
        budget.explicitly_shared = False
    except Exception:
        pass
    budget_response = budget_service.mutate_campaign_budgets(customer_id=cid, operations=[budget_operation])
    budget_resource = budget_response.results[0].resource_name

    campaign_service = client.get_service("CampaignService")
    campaign_operation = client.get_type("CampaignOperation")
    campaign = campaign_operation.create
    campaign.name = campaign_name
    campaign.status = client.enums.CampaignStatusEnum.PAUSED
    campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.DEMAND_GEN
    campaign.campaign_budget = budget_resource

    # Different API versions/accounts can require different bidding setup.
    # Target CPA is a common starter, but keep this as a shell for review.
    try:
        campaign.target_cpa.target_cpa_micros = _micros_from_dollars(target_cpa)
    except Exception:
        pass
    try:
        campaign.contains_eu_political_advertising = client.enums.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
    except Exception:
        pass
    try:
        campaign.start_date = date.today().strftime("%Y%m%d")
        campaign.end_date = (date.today() + timedelta(days=int(duration_days))).strftime("%Y%m%d")
    except Exception:
        pass

    campaign_response = campaign_service.mutate_campaigns(customer_id=cid, operations=[campaign_operation])
    campaign_resource = campaign_response.results[0].resource_name

    return {
        "campaign": campaign_resource,
        "budget": budget_resource,
        "status": "Created paused Demand Gen shell. Finish assets/ad group/audience in Google Ads before enabling.",
    }
