"""Paused Search campaign creation."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Dict, Iterable, List

from .google_ads_client import load_client, normalize_customer_id


def _micros_from_dollars(dollars: float) -> int:
    return int(round(float(dollars) * 1_000_000))


def _clean_list(values: Iterable[str], limit: int | None = None) -> List[str]:
    cleaned = [" ".join(str(v).split()) for v in values if " ".join(str(v).split())]
    return cleaned[:limit] if limit else cleaned


def create_paused_search_campaign(
    yaml_path: str,
    customer_id: str,
    campaign_name: str,
    daily_budget: float,
    final_url: str,
    keywords: List[str],
    headlines: List[str],
    descriptions: List[str],
    cpc_bid: float = 0.50,
    duration_days: int = 30,
) -> Dict:
    """Creates a paused Search campaign with one ad group and one responsive search ad."""
    client = load_client(yaml_path)
    cid = normalize_customer_id(customer_id)

    keyword_list = _clean_list(keywords, limit=80)
    headline_list = _clean_list(headlines, limit=15)
    description_list = _clean_list(descriptions, limit=4)

    if not cid:
        raise ValueError("Customer ID is required.")
    if not final_url.startswith(("http://", "https://")):
        raise ValueError("Final URL must start with http:// or https://")
    if not keyword_list:
        raise ValueError("Add at least one keyword.")
    if len(headline_list) < 3:
        raise ValueError("Add at least 3 headlines.")
    if len(description_list) < 2:
        raise ValueError("Add at least 2 descriptions.")

    budget_service = client.get_service("CampaignBudgetService")
    budget_operation = client.get_type("CampaignBudgetOperation")
    budget = budget_operation.create
    budget.name = f"{campaign_name} Budget {date.today().isoformat()}"
    budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
    budget.amount_micros = _micros_from_dollars(daily_budget)
    budget_response = budget_service.mutate_campaign_budgets(customer_id=cid, operations=[budget_operation])
    budget_resource = budget_response.results[0].resource_name

    campaign_service = client.get_service("CampaignService")
    campaign_operation = client.get_type("CampaignOperation")
    campaign = campaign_operation.create
    campaign.name = campaign_name
    campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
    campaign.status = client.enums.CampaignStatusEnum.PAUSED
    campaign.campaign_budget = budget_resource
    campaign.manual_cpc.enhanced_cpc_enabled = True
    try:
        campaign.contains_eu_political_advertising = client.enums.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
    except Exception:
        pass
    campaign.network_settings.target_google_search = True
    campaign.network_settings.target_search_network = True
    campaign.network_settings.target_content_network = False
    campaign.network_settings.target_partner_search_network = False
    campaign.start_date = date.today().strftime("%Y%m%d")
    campaign.end_date = (date.today() + timedelta(days=int(duration_days))).strftime("%Y%m%d")
    campaign_response = campaign_service.mutate_campaigns(customer_id=cid, operations=[campaign_operation])
    campaign_resource = campaign_response.results[0].resource_name

    ad_group_service = client.get_service("AdGroupService")
    ad_group_operation = client.get_type("AdGroupOperation")
    ad_group = ad_group_operation.create
    ad_group.name = f"{campaign_name} Ad Group"
    ad_group.campaign = campaign_resource
    ad_group.status = client.enums.AdGroupStatusEnum.ENABLED
    ad_group.type_ = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
    ad_group.cpc_bid_micros = _micros_from_dollars(cpc_bid)
    ad_group_response = ad_group_service.mutate_ad_groups(customer_id=cid, operations=[ad_group_operation])
    ad_group_resource = ad_group_response.results[0].resource_name

    criterion_service = client.get_service("AdGroupCriterionService")
    criterion_operations = []
    for keyword_text in keyword_list:
        operation = client.get_type("AdGroupCriterionOperation")
        criterion = operation.create
        criterion.ad_group = ad_group_resource
        criterion.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
        criterion.keyword.text = keyword_text
        criterion.keyword.match_type = client.enums.KeywordMatchTypeEnum.PHRASE
        criterion_operations.append(operation)
    criterion_service.mutate_ad_group_criteria(customer_id=cid, operations=criterion_operations)

    ad_group_ad_service = client.get_service("AdGroupAdService")
    ad_operation = client.get_type("AdGroupAdOperation")
    ad_group_ad = ad_operation.create
    ad_group_ad.ad_group = ad_group_resource
    ad_group_ad.status = client.enums.AdGroupAdStatusEnum.PAUSED
    ad = ad_group_ad.ad
    ad.final_urls.append(final_url)

    for text in headline_list:
        asset = client.get_type("AdTextAsset")
        asset.text = text[:30]
        ad.responsive_search_ad.headlines.append(asset)
    for text in description_list:
        asset = client.get_type("AdTextAsset")
        asset.text = text[:90]
        ad.responsive_search_ad.descriptions.append(asset)

    ad_response = ad_group_ad_service.mutate_ad_group_ads(customer_id=cid, operations=[ad_operation])
    ad_resource = ad_response.results[0].resource_name

    return {
        "campaign": campaign_resource,
        "budget": budget_resource,
        "ad_group": ad_group_resource,
        "responsive_search_ad": ad_resource,
        "status": "Created as paused for review.",
    }
