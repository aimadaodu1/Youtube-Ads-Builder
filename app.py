from __future__ import annotations

from datetime import datetime
import os
from pathlib import Path
from typing import List

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from campaign_blueprints import BLUEPRINTS, API_FULL, API_PARTIAL, get_blueprint
from copy_generator import generate_music_ad_copy
from exporter import brief_to_csv_bytes, brief_to_json_bytes, export_brief
from manual_pack import build_manual_launch_pack
from services.config_manager import (
    GOOGLE_ADS_YAML_PATH,
    has_google_ads_yaml,
    load_app_config,
    mask,
    normalize_customer_id,
    read_google_ads_yaml,
    save_app_config,
    save_google_ads_yaml,
)
from services.google_ads_client import format_google_ads_exception, test_connection
from services.oauth_setup import generate_refresh_token
from services.search_campaign import create_paused_search_campaign
from services.demand_gen_shell import create_paused_demand_gen_shell
from services.reporting import list_existing_video_campaigns
from template_store import delete_template, get_template, list_templates, save_template

load_dotenv()
st.set_page_config(page_title="YouTube Ads Builder", page_icon="▶️", layout="wide")


def lines(text: str) -> List[str]:
    return [line.strip() for line in str(text or "").splitlines() if line.strip()]


def _init_setup_state() -> None:
    if st.session_state.get("setup_state_loaded"):
        return
    app_config = load_app_config()
    yaml_path = app_config.get("yaml_path") or str(GOOGLE_ADS_YAML_PATH)
    yaml_values = read_google_ads_yaml(yaml_path)
    st.session_state["setup_yaml_path"] = yaml_path
    st.session_state["setup_developer_token"] = yaml_values.get("developer_token", "")
    st.session_state["setup_client_id"] = yaml_values.get("client_id", "")
    st.session_state["setup_client_secret"] = yaml_values.get("client_secret", "")
    st.session_state["setup_refresh_token"] = yaml_values.get("refresh_token", "")
    st.session_state["setup_login_customer_id"] = yaml_values.get("login_customer_id", app_config.get("login_customer_id", ""))
    st.session_state["setup_customer_id"] = app_config.get("customer_id", os.getenv("GOOGLE_ADS_CUSTOMER_ID", ""))
    st.session_state["setup_state_loaded"] = True


_init_setup_state()
app_config = load_app_config()

st.title("YouTube Ads Builder for Google Ads")
st.caption("Generate YouTube ad launch packs, save reusable music-ad templates, and create supported paused campaigns from one local app.")

with st.sidebar:
    st.header("Account status")
    current_yaml_path = st.session_state.get("setup_yaml_path") or app_config.get("yaml_path") or str(GOOGLE_ADS_YAML_PATH)
    current_customer_id = normalize_customer_id(st.session_state.get("setup_customer_id") or app_config.get("customer_id"))
    yaml_exists = has_google_ads_yaml(current_yaml_path)
    st.write("Credentials file:", "✅ saved" if yaml_exists else "⚠️ not saved")
    st.write("Customer ID:", f"`{current_customer_id}`" if current_customer_id else "⚠️ not set")
    st.caption("Use the Setup tab first if this is your first time.")
    st.divider()
    st.header("Saved templates")
    templates = list_templates()
    template_names = [t["name"] for t in templates]
    selected_template = st.selectbox("Load template", options=[""] + template_names)
    if selected_template and st.button("Load selected template"):
        template = get_template(selected_template)
        if template:
            st.session_state["loaded_template"] = template["brief"]
            st.success("Template loaded. Scroll to Campaign Builder.")

setup_tab, builder_tab, help_tab = st.tabs(["1. Setup / connect Google Ads", "2. Campaign Builder", "Help"])

with setup_tab:
    # Streamlit does not allow changing a widget key after the widget has been
    # rendered in the same run. OAuth generation happens after the text input is
    # already on screen, so we store the token in a temporary key, rerun, and
    # then apply it before rendering the Refresh token input.
    if st.session_state.get("pending_generated_refresh_token"):
        st.session_state["setup_refresh_token"] = st.session_state.pop("pending_generated_refresh_token")

    st.subheader("First-time setup wizard")
    st.write(
        "This page lets the app ask for the Google Ads credentials and save them locally. "
        "You only need to do this once per computer."
    )

    status_col1, status_col2, status_col3 = st.columns(3)
    with status_col1:
        st.metric("Credentials", "Saved" if yaml_exists else "Missing")
    with status_col2:
        st.metric("Customer ID", current_customer_id or "Missing")
    with status_col3:
        st.metric("YAML path", Path(current_yaml_path).name)

    st.warning(
        "Keep these credentials private. This app saves them on your own computer in the local config folder, not in the cloud."
    )

    st.markdown("### Step A: Enter your Google Ads API details")
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Developer token", type="password", key="setup_developer_token")
        st.text_input("OAuth client ID", key="setup_client_id")
        st.text_input("OAuth client secret", type="password", key="setup_client_secret")
    with c2:
        st.text_input("Refresh token", type="password", key="setup_refresh_token")
        st.text_input("Google Ads Customer ID", placeholder="123-456-7890", key="setup_customer_id")
        st.text_input(
            "Manager account ID / login_customer_id (optional)",
            placeholder="Only needed if you use a manager account",
            key="setup_login_customer_id",
        )

    with st.expander("I do not have a refresh token yet", expanded=not bool(st.session_state.get("setup_refresh_token"))):
        st.write(
            "Enter your OAuth client ID and client secret above, then click the button below. "
            "Your browser will open to Google. After you approve access, the app will paste the refresh token into the setup field."
        )
        st.info(
            "Use an OAuth Desktop App client in Google Cloud. The required scope is: https://www.googleapis.com/auth/adwords"
        )
        oauth_col1, oauth_col2 = st.columns([1, 2])
        with oauth_col1:
            if st.button("Generate refresh token", type="primary"):
                try:
                    token = generate_refresh_token(
                        st.session_state.get("setup_client_id", ""),
                        st.session_state.get("setup_client_secret", ""),
                    )
                    st.session_state["pending_generated_refresh_token"] = token
                    st.success("Refresh token generated. Reloading the setup form now...")
                    st.rerun()
                except Exception as ex:
                    st.error("Could not generate refresh token from inside the app.")
                    st.code(str(ex))
                    st.write("Backup option: run this in Command Prompt from the app folder:")
                    st.code("python generate_refresh_token.py")
        with oauth_col2:
            st.caption(
                "If Google says the app is unverified, that can happen while your OAuth app is still in testing mode. "
                "Use your own Google account as a test user in Google Cloud."
            )

    st.markdown("### Step B: Save and test")
    save_col, test_col = st.columns(2)
    with save_col:
        if st.button("Save credentials locally", type="primary"):
            try:
                yaml_path = save_google_ads_yaml(
                    developer_token=st.session_state.get("setup_developer_token", ""),
                    client_id=st.session_state.get("setup_client_id", ""),
                    client_secret=st.session_state.get("setup_client_secret", ""),
                    refresh_token=st.session_state.get("setup_refresh_token", ""),
                    login_customer_id=st.session_state.get("setup_login_customer_id", ""),
                )
                save_app_config(
                    customer_id=st.session_state.get("setup_customer_id", ""),
                    yaml_path=str(yaml_path),
                    login_customer_id=st.session_state.get("setup_login_customer_id", ""),
                )
                st.session_state["setup_yaml_path"] = str(yaml_path)
                st.success(f"Saved credentials to {yaml_path}")
            except Exception as ex:
                st.error("Save failed.")
                st.code(str(ex))
    with test_col:
        if st.button("Test Google Ads connection"):
            try:
                result = test_connection(
                    st.session_state.get("setup_yaml_path") or str(GOOGLE_ADS_YAML_PATH),
                    normalize_customer_id(st.session_state.get("setup_customer_id", "")),
                )
                st.success(result["message"])
                st.write("Accessible accounts:")
                st.json(result["accessible_customers"])
                if result.get("campaign_count") is not None:
                    st.write("Campaign rows readable:", result["campaign_count"])
            except Exception as ex:
                st.error("Connection failed.")
                st.code(format_google_ads_exception(ex))

    with st.expander("What is currently saved?", expanded=False):
        saved = read_google_ads_yaml(st.session_state.get("setup_yaml_path") or str(GOOGLE_ADS_YAML_PATH))
        st.write({
            "developer_token": mask(saved.get("developer_token", "")),
            "client_id": mask(saved.get("client_id", "")),
            "client_secret": mask(saved.get("client_secret", "")),
            "refresh_token": mask(saved.get("refresh_token", "")),
            "login_customer_id": saved.get("login_customer_id", ""),
            "customer_id": normalize_customer_id(st.session_state.get("setup_customer_id", "")),
        })

with builder_tab:
    loaded = st.session_state.get("loaded_template", {}) or {}
    st.subheader("1. Choose ad type")
    ad_type_default = loaded.get("ad_type") if loaded.get("ad_type") in BLUEPRINTS else "Video Views"
    ad_type = st.selectbox(
        "Ad type",
        options=list(BLUEPRINTS.keys()),
        index=list(BLUEPRINTS.keys()).index(ad_type_default),
    )
    blueprint = get_blueprint(ad_type)

    col_a, col_b, col_c = st.columns([1.1, 1.1, 1])
    with col_a:
        st.markdown("**Recommended Google Ads route**")
        st.write(blueprint.recommended_campaign_type)
    with col_b:
        st.markdown("**Creation mode**")
        st.code(blueprint.api_creation_mode)
    with col_c:
        st.markdown("**Bid note**")
        st.write(blueprint.default_bid_note)

    with st.expander("What this tool can do for this ad type", expanded=False):
        st.markdown("**App can do:**")
        for item in blueprint.what_app_can_do:
            st.write(f"- {item}")
        st.markdown("**Manual review/setup steps:**")
        for item in blueprint.manual_steps:
            st.write(f"- {item}")
        if blueprint.notes:
            st.markdown("**Notes:**")
            for item in blueprint.notes:
                st.write(f"- {item}")

    st.subheader("2. Enter campaign details")
    left, right = st.columns(2)
    with left:
        campaign_name = st.text_input("Campaign name", value=loaded.get("campaign_name", "Sympar YouTube Campaign"))
        artist_name = st.text_input("Artist name", value=loaded.get("artist_name", "Sympar"))
        song_title = st.text_input("Song/video title", value=loaded.get("song_title", "MA$E MARGIELA"))
        genre = st.text_input("Genre", value=loaded.get("genre", "Afrobeats / Rap"))
        mood = st.text_input("Mood / angle", value=loaded.get("mood", "high-energy"))
        youtube_url = st.text_input("YouTube video URL", value=loaded.get("youtube_url", ""), placeholder="https://www.youtube.com/watch?v=...")
        final_url = st.text_input("Landing page / final URL", value=loaded.get("final_url", ""), placeholder="https://link-to-song-or-video.com")

    with right:
        daily_budget = st.number_input("Daily budget ($)", min_value=1.0, value=float(loaded.get("daily_budget_usd", 10.0)), step=1.0)
        target_cpa = st.number_input("Target CPA for Demand Gen shell ($)", min_value=0.5, value=float(loaded.get("target_cpa_usd", 1.0)), step=0.5)
        cpc_bid = st.number_input("Max CPC for Search ($)", min_value=0.05, value=float(loaded.get("cpc_bid_usd", 0.50)), step=0.05)
        cpv_bid = st.number_input("Planned CPV bid for video launch pack ($)", min_value=0.001, value=float(loaded.get("cpv_bid_usd", 0.03)), step=0.001, format="%.3f")
        duration_days = st.number_input("Campaign duration days", min_value=1, value=int(loaded.get("duration_days", 30)), step=1)
        countries_text = st.text_area(
            "Countries/locations, one per line",
            value="\n".join(loaded.get("countries", ["United States", "United Kingdom", "Canada", "Nigeria", "Ghana"])),
            height=130,
        )
        targets_text = st.text_area(
            "Artist/channel/interest targets, one per line",
            value="\n".join(loaded.get("targets", ["Burna Boy", "Wizkid", "Rema", "Asake", "Afrobeats"])),
            height=130,
        )

    st.subheader("3. Generate copy and targeting")
    release_note = st.text_area(
        "Optional release note / positioning",
        value=loaded.get("release_note", "A fresh Afrobeats and rap release with a polished visual and strong hook."),
    )
    copy = generate_music_ad_copy(artist_name, song_title, genre, mood, release_note)

    headline_default = "\n".join(loaded.get("headlines", copy.headlines))
    description_default = "\n".join(loaded.get("descriptions", copy.descriptions))
    hook_default = "\n".join(loaded.get("video_hooks", copy.video_hooks))

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Headlines**")
        edited_headlines = st.text_area("Edit headlines", value=headline_default, height=260)
    with col2:
        st.markdown("**Descriptions**")
        edited_descriptions = st.text_area("Edit descriptions", value=description_default, height=260)
    with col3:
        st.markdown("**First-five-seconds hooks**")
        edited_hooks = st.text_area("Edit video hooks", value=hook_default, height=260)

    keywords_default = loaded.get("keywords") or [
        f"{artist_name} {song_title}".strip(),
        f"{song_title} official video".strip(),
        f"new {genre} music".strip(),
        "afrobeats music video",
        "new nigerian music",
    ]
    keywords_text = st.text_area("Search keywords, one per line", value="\n".join(keywords_default), height=110)

    brief = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "ad_type": ad_type,
        "api_creation_mode": blueprint.api_creation_mode,
        "recommended_campaign_type": blueprint.recommended_campaign_type,
        "campaign_name": campaign_name,
        "artist_name": artist_name,
        "song_title": song_title,
        "genre": genre,
        "mood": mood,
        "release_note": release_note,
        "youtube_url": youtube_url,
        "final_url": final_url,
        "daily_budget_usd": daily_budget,
        "duration_days": int(duration_days),
        "target_cpa_usd": target_cpa,
        "cpc_bid_usd": cpc_bid,
        "cpv_bid_usd": cpv_bid,
        "bid_note": blueprint.default_bid_note,
        "countries": lines(countries_text),
        "targets": lines(targets_text),
        "headlines": lines(edited_headlines),
        "descriptions": lines(edited_descriptions),
        "video_hooks": lines(edited_hooks),
        "keywords": lines(keywords_text),
        "short_calls_to_action": copy.short_ctas,
        "manual_steps": blueprint.manual_steps,
        "notes": blueprint.notes,
    }
    launch_pack_text = build_manual_launch_pack(brief)

    st.subheader("4. Review and act")
    tab_summary, tab_pack, tab_templates, tab_export, tab_api, tab_browser, tab_reports = st.tabs([
        "Summary", "Launch pack", "Templates", "Export", "API actions", "Browser assist", "Reports"
    ])

    with tab_summary:
        rows = [
            {"Field": "Ad type", "Value": brief["ad_type"]},
            {"Field": "Campaign route", "Value": brief["recommended_campaign_type"]},
            {"Field": "Creation mode", "Value": brief["api_creation_mode"]},
            {"Field": "Budget", "Value": f"${daily_budget:.2f}/day"},
            {"Field": "Planned CPV", "Value": f"${cpv_bid:.3f}"},
            {"Field": "YouTube URL", "Value": youtube_url or "Not set"},
            {"Field": "Final URL", "Value": final_url or "Not set"},
            {"Field": "Countries", "Value": ", ".join(brief["countries"])},
            {"Field": "Targets", "Value": ", ".join(brief["targets"])},
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.markdown("**Checklist**")
        for step in brief["manual_steps"]:
            st.checkbox(step, value=False)

    with tab_pack:
        st.text_area("Copy/paste launch pack", value=launch_pack_text, height=520)
        st.download_button(
            "Download launch pack .txt",
            data=launch_pack_text.encode("utf-8"),
            file_name=f"{campaign_name.replace(' ', '_')}_launch_pack.txt",
            mime="text/plain",
        )

    with tab_templates:
        st.write("Save this setup so the app remembers your repeated music-ad workflow.")
        template_name = st.text_input("Template name", value=campaign_name)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Save/update template"):
                save_template(template_name, brief)
                st.success("Template saved locally.")
        with c2:
            if selected_template and st.button("Delete selected template"):
                delete_template(selected_template)
                st.success("Template deleted. Refresh the app to update the dropdown.")
        st.markdown("**Existing templates**")
        st.dataframe(pd.DataFrame([{ "name": t["name"], "updated_at": t.get("updated_at", "") } for t in list_templates()]), use_container_width=True, hide_index=True)

    with tab_export:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button("Download JSON", data=brief_to_json_bytes(brief), file_name=f"{campaign_name.replace(' ', '_')}.json", mime="application/json")
        with c2:
            st.download_button("Download CSV", data=brief_to_csv_bytes(brief), file_name=f"{campaign_name.replace(' ', '_')}.csv", mime="text/csv")
        with c3:
            if st.button("Save files to exports folder"):
                json_path, csv_path = export_brief(brief, campaign_name)
                st.success("Exported campaign brief.")
                st.write("JSON:", json_path)
                st.write("CSV:", csv_path)

    with tab_api:
        st.warning("API actions create paused campaigns only. Review inside Google Ads before enabling anything.")
        yaml_path_for_api = st.session_state.get("setup_yaml_path") or str(GOOGLE_ADS_YAML_PATH)
        customer_id_for_api = normalize_customer_id(st.session_state.get("setup_customer_id") or load_app_config().get("customer_id", ""))
        st.caption(f"Using Customer ID: {customer_id_for_api or 'not set'}")

        if not has_google_ads_yaml(yaml_path_for_api) or not customer_id_for_api:
            st.error("Finish the Setup tab before using API actions.")
        elif blueprint.api_creation_mode == API_FULL:
            st.markdown("**Create paused Search campaign**")
            if st.button("Create paused Search campaign in Google Ads"):
                try:
                    result = create_paused_search_campaign(
                        yaml_path=yaml_path_for_api,
                        customer_id=customer_id_for_api,
                        campaign_name=campaign_name,
                        daily_budget=daily_budget,
                        final_url=final_url,
                        keywords=brief["keywords"],
                        headlines=brief["headlines"],
                        descriptions=brief["descriptions"],
                        cpc_bid=cpc_bid,
                        duration_days=int(duration_days),
                    )
                    st.success("Search campaign created as paused.")
                    st.json(result)
                except Exception as ex:
                    st.error("Creation failed.")
                    st.code(format_google_ads_exception(ex))
        elif blueprint.api_creation_mode == API_PARTIAL:
            st.markdown("**Create paused Demand Gen shell**")
            st.info("This creates the paused campaign + budget foundation. Finish assets, ad group, audience, and channel controls in Google Ads before enabling.")
            if st.button("Create paused Demand Gen shell"):
                try:
                    result = create_paused_demand_gen_shell(
                        yaml_path=yaml_path_for_api,
                        customer_id=customer_id_for_api,
                        campaign_name=campaign_name,
                        daily_budget=daily_budget,
                        target_cpa=target_cpa,
                        duration_days=int(duration_days),
                    )
                    st.success("Demand Gen shell created as paused.")
                    st.json(result)
                except Exception as ex:
                    st.error("Creation failed.")
                    st.code(format_google_ads_exception(ex))
        else:
            st.markdown("**Manual/API limitation mode**")
            st.info("For this ad type, Google Ads API does not support full classic VIDEO campaign creation. Use the launch pack and Browser Assist tab.")

    with tab_browser:
        st.markdown("**Browser assist for Video Views, skippable, non-skippable, and in-feed setups**")
        st.write("This opens Google Ads with a persistent browser profile so you can use the launch pack faster. You can also record a manual campaign setup once with Playwright codegen.")
        st.code("python browser_automation/open_google_ads.py --customer-id " + (current_customer_id or "1234567890"))
        st.code("playwright codegen https://ads.google.com/aw/campaigns/new")
        st.write("Files included:")
        st.write("- browser_automation/open_google_ads.py")
        st.write("- browser_automation/record_google_ads_flow.bat")
        st.write("- browser_automation/record_google_ads_flow.sh")
        st.info("Use browser automation carefully. Google Ads UI changes often, and you should keep campaigns paused until you review the final setup.")

    with tab_reports:
        st.markdown("**Existing classic VIDEO campaign reporting**")
        st.write("Because the API can fetch/report on existing VIDEO campaigns, this tab can list your existing video campaigns after you create them in Google Ads.")
        if st.button("List existing VIDEO campaigns"):
            try:
                rows = list_existing_video_campaigns(
                    st.session_state.get("setup_yaml_path") or str(GOOGLE_ADS_YAML_PATH),
                    normalize_customer_id(st.session_state.get("setup_customer_id") or load_app_config().get("customer_id", "")),
                    limit=20,
                )
                if rows:
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                else:
                    st.info("No existing VIDEO campaigns returned.")
            except Exception as ex:
                st.error("Report failed.")
                st.code(format_google_ads_exception(ex))

with help_tab:
    st.subheader("How this app works")
    st.write(
        "The Setup tab saves your API credentials locally so the Campaign Builder can connect to your Google Ads account. "
        "For classic YouTube Video campaigns such as Video Views, skippable, and non-skippable, the app generates a launch pack and browser-assist flow because those campaign types are not fully creatable through the Google Ads API."
    )
    st.markdown("### What each action means")
    st.write("**Launch pack:** a complete copy/paste plan for settings, countries, targets, ad copy, bidding, and review steps.")
    st.write("**Paused Search campaign:** a real Search campaign created in Google Ads as paused.")
    st.write("**Paused Demand Gen shell:** a Demand Gen campaign foundation created as paused, then finished in the Google Ads UI.")
    st.write("**Browser assist:** opens Google Ads and lets you record/replay parts of the manual UI setup with Playwright.")
    st.markdown("### Files to keep private")
    st.code("config/google-ads.yaml\nconfig/app_config.json")

st.divider()
st.caption("Keep campaigns paused until you verify policy status, budget, targeting, placements, assets, final URLs, and billing inside Google Ads.")
