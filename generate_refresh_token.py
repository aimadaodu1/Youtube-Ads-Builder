"""Backup CLI helper if Streamlit's in-app OAuth button does not work on your PC."""
from __future__ import annotations

from getpass import getpass

from services.oauth_setup import generate_refresh_token

print("Google Ads OAuth Refresh Token Helper")
print("Paste your OAuth client ID and secret from Google Cloud.")
client_id = input("OAuth client ID: ").strip()
client_secret = getpass("OAuth client secret: ").strip()
print("\nOpening browser sign-in...")
token = generate_refresh_token(client_id, client_secret)
print("\nRefresh token generated. Copy this into the app setup wizard:")
print(token)
