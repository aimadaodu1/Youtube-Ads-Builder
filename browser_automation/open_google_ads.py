"""Browser helper for UI-only video campaign types.

This opens Google Ads in a persistent Playwright browser profile. It does not
try to bypass Google's UI or policies. Use it to log in once, keep the session,
and optionally build your own replay script after recording your clicks.
"""
from __future__ import annotations

from pathlib import Path
import argparse

from playwright.sync_api import sync_playwright


def open_google_ads(customer_id: str | None = None, url: str | None = None) -> None:
    profile_dir = Path(__file__).parent / "google_profile"
    profile_dir.mkdir(exist_ok=True)
    target = url or "https://ads.google.com/aw/campaigns/new"
    if customer_id:
        # Google may ignore this if the UI route changes, but it is useful when supported.
        target = f"https://ads.google.com/aw/campaigns/new?ocid={customer_id}"

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=False,
            viewport={"width": 1440, "height": 1000},
        )
        page = browser.new_page()
        page.goto(target, wait_until="domcontentloaded")
        print("Browser opened. Log in and use the generated launch pack to complete setup.")
        print("Close the browser window when finished.")
        page.wait_for_timeout(24 * 60 * 60 * 1000)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--customer-id", default=None)
    parser.add_argument("--url", default=None)
    args = parser.parse_args()
    open_google_ads(customer_id=args.customer_id, url=args.url)
