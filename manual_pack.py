"""Manual launch pack generation for UI-only video campaign types."""
from __future__ import annotations

from typing import Dict, List


def _bullets(items: List[str]) -> str:
    return "\n".join(f"- {item}" for item in items if item)


def build_manual_launch_pack(brief: Dict) -> str:
    countries = _bullets(brief.get("countries", []))
    targets = _bullets(brief.get("targets", []))
    headlines = _bullets(brief.get("headlines", []))
    descriptions = _bullets(brief.get("descriptions", []))
    hooks = _bullets(brief.get("video_hooks", []))
    manual_steps = _bullets(brief.get("manual_steps", []))
    notes = _bullets(brief.get("notes", []))

    return f"""
# Google Ads Launch Pack

## Campaign
Campaign name: {brief.get('campaign_name', '')}
Ad type: {brief.get('ad_type', '')}
Recommended route: {brief.get('recommended_campaign_type', '')}
Budget: ${brief.get('daily_budget_usd', '')}/day
Duration: {brief.get('duration_days', '')} days
Bid note: {brief.get('bid_note', '')}

## Creative
Artist: {brief.get('artist_name', '')}
Song/video: {brief.get('song_title', '')}
Genre: {brief.get('genre', '')}
Mood/angle: {brief.get('mood', '')}
YouTube URL: {brief.get('youtube_url', '')}
Final URL: {brief.get('final_url', '')}

## Countries
{countries}

## Targeting ideas
{targets}

## Headlines
{headlines}

## Descriptions
{descriptions}

## First-five-seconds hooks
{hooks}

## Manual setup checklist
{manual_steps}

## Notes
{notes}

## Launch rule
Keep the campaign paused until you verify video preview, budget, targeting, final URL, policy status, and conversion settings inside Google Ads.
""".strip()
