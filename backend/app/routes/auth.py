"""
Auth routes: Google OAuth 2.0 login and callback.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from app.services.oauth_service import get_oauth_service
from app.utils.logger import get_logger

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = get_logger(__name__)


@router.get("/login", summary="Initiate Google OAuth login")
async def login():
    """Redirect the user to Google's OAuth consent screen."""
    oauth = get_oauth_service()
    auth_url, state = oauth.get_authorization_url()
    logger.info({"action": "oauth_login_initiated"})
    return RedirectResponse(url=auth_url)


@router.get("/callback", summary="Google OAuth callback")
async def callback(code: str, state: str | None = None, error: str | None = None):
    """Handle the OAuth callback and exchange code for tokens."""
    if error:
        logger.error({"action": "oauth_callback_error", "error": error})
        raise HTTPException(status_code=401, detail=f"OAuth error: {error}")

    oauth = get_oauth_service()
    try:
        creds = oauth.exchange_code(code)
        logger.info({"action": "oauth_callback_success"})
        return {"message": "Authentication successful. You can now use the API.", "authenticated": True}
    except Exception as e:
        logger.error({"action": "oauth_exchange_failed", "error": str(e)})
        raise HTTPException(status_code=401, detail=f"Token exchange failed: {e}")
