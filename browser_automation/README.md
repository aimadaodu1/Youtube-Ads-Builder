# Browser automation helper

Google Ads API cannot create/update classic VIDEO campaigns, so this folder gives you a safe UI-assist path.

## Open Google Ads with a saved browser profile

```bash
python browser_automation/open_google_ads.py --customer-id 1234567890
```

This opens Chromium with a persistent local profile stored in:

```text
browser_automation/google_profile/
```

Log in once, then the browser can remember your Google session.

## Record your manual setup once

After installing Playwright browsers:

```bash
python -m playwright install chromium
playwright codegen https://ads.google.com/aw/campaigns/new
```

Create a Video Views campaign manually while Playwright records selectors. Save the generated script as your own replay script.

Important: Google Ads UI changes often. Review any replay script before using it and keep campaigns paused until you check everything.
