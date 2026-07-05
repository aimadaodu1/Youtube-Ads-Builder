"""Definitions for each ad type the app can prepare."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class CampaignBlueprint:
    ad_type: str
    api_creation_mode: str
    recommended_campaign_type: str
    objective: str
    default_bid_note: str
    what_app_can_do: List[str]
    manual_steps: List[str]
    notes: List[str]


API_FULL = "fully_supported"
API_PARTIAL = "partially_supported_starter_shell"
MANUAL = "manual_launch_pack"
BROWSER_ASSIST = "browser_assisted_manual"


BLUEPRINTS: Dict[str, CampaignBlueprint] = {
    "Demand Gen YouTube-focused": CampaignBlueprint(
        ad_type="Demand Gen YouTube-focused",
        api_creation_mode=API_PARTIAL,
        recommended_campaign_type="Demand Gen with YouTube-focused channel controls",
        objective="Show video/image ads across YouTube and other visual Google surfaces, with YouTube focus when configured.",
        default_bid_note="Start with a small daily budget and conservative target CPA until you see quality signals.",
        what_app_can_do=[
            "Generate music/video copy, hooks, targeting notes, and launch checklist.",
            "Create a paused Demand Gen campaign shell if your account/API version supports it.",
            "Export a clean setup pack for final creative/audience setup in Google Ads.",
        ],
        manual_steps=[
            "Open the paused Demand Gen campaign in Google Ads.",
            "Add/confirm YouTube video asset, final URL, logo/image assets, and business name.",
            "Set channel controls if you want YouTube-only, Shorts-focused, or broader inventory.",
            "Review locations, languages, budget, brand safety, and conversion settings.",
            "Enable only after previews and policy checks look right.",
        ],
        notes=[
            "Demand Gen is the practical API-supported path for YouTube-style programmatic creation.",
            "Channel-control availability can vary by account and API version.",
        ],
    ),
    "Video Views": CampaignBlueprint(
        ad_type="Video Views",
        api_creation_mode=BROWSER_ASSIST,
        recommended_campaign_type="Video campaign in Google Ads UI, or Demand Gen alternative",
        objective="Maximize YouTube video views.",
        default_bid_note="Use Max CPV or the UI's recommended video-views bidding. Start low, then increase if delivery is too slow.",
        what_app_can_do=[
            "Generate copy, targeting, budget notes, CPV fields, and a click-by-click launch checklist.",
            "Export your campaign pack as JSON/CSV.",
            "Open a browser automation helper so you can record/replay the UI flow later.",
            "Report on existing VIDEO campaigns after they exist in the account.",
        ],
        manual_steps=[
            "Create a Video Views campaign in the Google Ads UI.",
            "Paste your YouTube URL and choose the video/ad format options available in the wizard.",
            "Enter the generated locations, interests, artist targets, copy, budget, and CPV settings.",
            "Keep it paused until previews and policy checks look right.",
        ],
        notes=["Classic VIDEO campaign creation/update is not exposed through the Google Ads API."],
    ),
    "In-feed video ad": CampaignBlueprint(
        ad_type="In-feed video ad",
        api_creation_mode=BROWSER_ASSIST,
        recommended_campaign_type="Video campaign in Google Ads UI, or Demand Gen with in-feed channel control",
        objective="Get interested viewers to click from YouTube feed/search-like surfaces into the video.",
        default_bid_note="Often better for intentional music views because the viewer chooses to click.",
        what_app_can_do=[
            "Generate in-feed headline/description options.",
            "Generate channel/artist/interest targeting and country lists.",
            "Export a manual launch pack and open the browser helper.",
        ],
        manual_steps=[
            "Create the campaign/ad group in the Google Ads UI or use Demand Gen if it fits your goal.",
            "Select in-feed format or channel controls where available.",
            "Confirm thumbnail, headline, and video preview before enabling.",
        ],
        notes=["Good for music because viewers intentionally click into the video."],
    ),
    "Skippable in-stream": CampaignBlueprint(
        ad_type="Skippable in-stream",
        api_creation_mode=BROWSER_ASSIST,
        recommended_campaign_type="Video campaign in Google Ads UI, or Demand Gen if it fits your goal",
        objective="Reach users before/during videos with a skippable ad.",
        default_bid_note="Keep the first five seconds strong. Optimize around engaged views, not just cheap impressions.",
        what_app_can_do=[
            "Generate script hooks and targeting notes.",
            "Export launch checklist and browser-assist pack.",
        ],
        manual_steps=[
            "Create the campaign in the Google Ads UI.",
            "Choose skippable in-stream where available.",
            "Use the first five seconds for the song hook, artist name, and visual identity.",
        ],
        notes=["Good for reach, but quality depends heavily on the opening seconds."],
    ),
    "Non-skippable in-stream": CampaignBlueprint(
        ad_type="Non-skippable in-stream",
        api_creation_mode=BROWSER_ASSIST,
        recommended_campaign_type="Video campaign in Google Ads UI",
        objective="Force full short-form exposure, usually for awareness.",
        default_bid_note="Use carefully because forced views can look strong but produce weaker engagement.",
        what_app_can_do=[
            "Generate short video hook/script ideas.",
            "Export setup checklist and browser-assist pack.",
        ],
        manual_steps=[
            "Create the campaign manually in Google Ads UI.",
            "Use a short, polished cut with the song hook immediately.",
            "Watch likes, comments, earned views, and retention, not just impressions.",
        ],
        notes=["Useful for awareness, but not always the best first campaign for music engagement."],
    ),
    "YouTube Shorts-style Demand Gen": CampaignBlueprint(
        ad_type="YouTube Shorts-style Demand Gen",
        api_creation_mode=API_PARTIAL,
        recommended_campaign_type="Demand Gen with Shorts-focused channel control",
        objective="Push vertical creative into Shorts-style inventory where available.",
        default_bid_note="Start with vertical creative and monitor hook retention/engagement quality closely.",
        what_app_can_do=[
            "Generate a Shorts-focused campaign brief.",
            "Create a paused Demand Gen shell if supported.",
            "Export checklist for Shorts/channel control setup.",
        ],
        manual_steps=[
            "Use vertical 9:16 creative.",
            "Confirm Shorts channel controls or placement behavior in Google Ads.",
            "Preview all assets before enabling.",
        ],
        notes=["Use a strong opening frame and hook within one to two seconds."],
    ),
    "Search campaign for video/song": CampaignBlueprint(
        ad_type="Search campaign for video/song",
        api_creation_mode=API_FULL,
        recommended_campaign_type="Search campaign",
        objective="Capture people searching artist, song, genre, playlist, or similar music terms.",
        default_bid_note="Start with phrase match and low CPC. Add negatives after checking search terms.",
        what_app_can_do=[
            "Create paused Search campaign, budget, ad group, keywords, and responsive search ad.",
            "Generate Search-friendly copy and keywords.",
        ],
        manual_steps=[
            "Review keywords and policy status in Google Ads.",
            "Add negative keywords if needed.",
            "Enable after final review.",
        ],
        notes=["This is not a YouTube video ad format, but it can send Search traffic to your video or landing page."],
    ),
}


def get_blueprint(ad_type: str) -> CampaignBlueprint:
    return BLUEPRINTS[ad_type]
