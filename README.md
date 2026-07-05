# YouTube Ads Builder v3

A local Streamlit app for building repeatable YouTube ad workflows for Google Ads.

## What changed in v3

This version includes an in-app setup wizard. You no longer need to manually edit `google-ads.yaml` unless you want to.

The app asks for:

- Google Ads developer token
- OAuth client ID
- OAuth client secret
- Refresh token
- Google Ads customer ID
- Optional manager account ID / `login_customer_id`

It saves credentials locally to:

```text
config/google-ads.yaml
config/app_config.json
```

Keep those files private.

## What the app does

- Creates launch packs for Video Views, skippable, non-skippable, in-feed, and Shorts-style ad workflows.
- Saves reusable campaign templates.
- Generates music-ad headlines, descriptions, first-five-seconds hooks, keywords, and checklist items.
- Exports JSON, CSV, and TXT launch packs.
- Tests your Google Ads API connection.
- Creates supported campaigns as paused where practical:
  - Search campaigns: fuller API creation path.
  - Demand Gen: paused campaign shell path.
- Lists existing classic Video campaigns for reporting.
- Includes Browser Assist scripts using Playwright for UI-only setup paths.

## Important Google Ads API limitation

Classic Google Ads Video campaigns, including many Video Views, skippable, non-skippable, and in-feed workflows, cannot be fully created or updated with the Google Ads API. The app handles those as launch packs and browser-assist workflows. Demand Gen and Search have better API-supported creation paths.

## Run on Windows

1. Install Python from https://www.python.org/downloads/
2. Extract this folder.
3. Double-click `run_windows.bat`.

Or use Command Prompt:

```bat
cd youtube_ads_builder_v3
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
streamlit run app.py
```

## First setup inside the app

1. Open the **Setup / connect Google Ads** tab.
2. Paste your developer token, OAuth client ID, OAuth client secret, and customer ID.
3. Click **Generate refresh token** if you do not already have one.
4. Approve Google Ads access in the browser.
5. Click **Save credentials locally**.
6. Click **Test Google Ads connection**.

If the in-app refresh-token flow does not work, run:

```bat
python generate_refresh_token.py
```

Then paste the token into the app.

## Safety defaults

The app is designed to create API-created campaigns as **paused**, so you can review them inside Google Ads before any money is spent.

## v3.1 refresh-token fix

This build fixes a Streamlit state issue where the refresh token could be generated successfully but the app could not paste it into the Refresh token field because Streamlit blocks changing a widget value after it has already rendered. The app now stores the token temporarily, reloads the setup form, and then fills the field.
