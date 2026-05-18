"""
Google OAuth 2.0 service.
Handles authorization URL generation, token exchange, refresh, and storage.
"""
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]

# Simple file-based token store (swap for DB/Redis in production)
TOKEN_FILE = Path(".token_store.json")


def _load_token_store() -> dict:
    if TOKEN_FILE.exists():
        return json.loads(TOKEN_FILE.read_text())
    return {}


def _save_token_store(store: dict) -> None:
    TOKEN_FILE.write_text(json.dumps(store))


class OAuthService:
    def __init__(self):
        self.settings = get_settings()

    def _build_flow(self) -> Flow:
        client_config = {
            "web": {
                "client_id": self.settings.google_client_id,
                "client_secret": self.settings.google_client_secret,
                "redirect_uris": [self.settings.google_redirect_uri],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }
        flow = Flow.from_client_config(client_config, scopes=SCOPES)
        flow.redirect_uri = self.settings.google_redirect_uri
        return flow

    def get_authorization_url(self) -> tuple[str, str]:
        """Returns (auth_url, state)."""
        flow = self._build_flow()
        auth_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        return auth_url, state

    def exchange_code(self, code: str) -> Credentials:
        """Exchange authorization code for credentials and persist them."""
        flow = self._build_flow()
        flow.fetch_token(code=code)
        creds = flow.credentials
        self._store_credentials("default", creds)
        logger.info({"action": "oauth_exchange", "status": "success"})
        return creds

    def get_credentials(self, user_id: str = "default") -> Credentials | None:
        """Load and auto-refresh credentials for a user."""
        store = _load_token_store()
        if user_id not in store:
            return None

        creds = Credentials(
            token=store[user_id].get("token"),
            refresh_token=store[user_id].get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.settings.google_client_id,
            client_secret=self.settings.google_client_secret,
            scopes=SCOPES,
        )

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            self._store_credentials(user_id, creds)
            logger.info({"action": "oauth_refresh", "user": user_id})

        return creds

    def _store_credentials(self, user_id: str, creds: Credentials) -> None:
        store = _load_token_store()
        store[user_id] = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
        }
        _save_token_store(store)


def get_oauth_service() -> OAuthService:
    return OAuthService()
