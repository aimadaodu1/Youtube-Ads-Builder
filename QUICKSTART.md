# Quickstart

## 1. Install Python

Download Python for Windows from:

```text
https://www.python.org/downloads/
```

During installation, check:

```text
Add python.exe to PATH
```

## 2. Start the app

Open Command Prompt in this folder and run:

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
streamlit run app.py
```

Windows shortcut:

```bat
run_windows.bat
```

## 3. Connect Google Ads inside the app

In the browser window that opens, go to:

```text
1. Setup / connect Google Ads
```

Fill in:

```text
Developer token
OAuth client ID
OAuth client secret
Refresh token
Google Ads Customer ID
```

If you do not have a refresh token, click:

```text
Generate refresh token
```

Then click:

```text
Save credentials locally
Test Google Ads connection
```

## 4. Build a campaign

Go to:

```text
2. Campaign Builder
```

Choose an ad type:

```text
Demand Gen
Video Views
In-feed video ad
Skippable in-stream
Non-skippable in-stream
YouTube Shorts-style Demand Gen
Search campaign for video/song
```

Enter your YouTube URL, budget, countries, targets, headlines, descriptions, and click the action you need.

## 5. What happens after that

For Search and supported Demand Gen foundations, the app can create paused campaigns in Google Ads.

For classic YouTube Video campaigns, the app generates a launch pack because the Google Ads API does not fully create those campaign types. Use the launch pack with the Browser Assist tab.
