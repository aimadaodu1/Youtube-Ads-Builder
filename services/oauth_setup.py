"""OAuth helper for generating a Google Ads refresh token inside the local app."""
from __future__ import annotations

from typing import Dict, List

SCOPES: List[str] = ["https://www.googleapis.com/auth/adwords"]


def build_installed_app_client_config(client_id: str, client_secret: str) -> Dict:
    return {
        "installed": {
            "client_id": client_id.strip(),
            "client_secret": client_secret.strip(),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": ["http://localhost"],
        }
    }


def generate_refresh_token(client_id: str, client_secret: str, port: int = 0) -> str:
    """Open a browser login flow and return a refresh token.

    This is intended for local use only. It starts a temporary localhost callback
    server, opens Google login, and waits until the user grants access.
    """
    if not client_id.strip() or not client_secret.strip():
        raise ValueError("OAuth client ID and client secret are required.")

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except Exception as exc:  # pragma: no cover - dependency availability
        raise RuntimeError("google-auth-oauthlib is not installed. Run: pip install -r requirements.txt") from exc

    flow = InstalledAppFlow.from_client_config(
        build_installed_app_client_config(client_id, client_secret),
        scopes=SCOPES,
    )
    credentials = flow.run_local_server(
        port=port,
        prompt="consent",
        authorization_prompt_message="Your browser will open so you can approve Google Ads access.",
        success_message="Authentication complete. You can close this browser tab and return to YouTube Ads Builder.",
        open_browser=True,
    )
    if not credentials.refresh_token:
        raise RuntimeError(
            "Google returned no refresh token. In Google Cloud, make sure your OAuth app is in testing/published mode and try again with prompt=consent."
        )
    return credentials.refresh_token
