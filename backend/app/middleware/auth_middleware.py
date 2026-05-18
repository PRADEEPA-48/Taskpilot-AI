"""
Authentication middleware.
Validates that credentials exist before protected routes are accessed.
"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.oauth_service import OAuthService
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Routes that do NOT require authentication
PUBLIC_PATHS = {"/health", "/auth/login", "/auth/callback", "/docs", "/openapi.json", "/redoc"}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Allow public paths through
        if any(path.startswith(p) for p in PUBLIC_PATHS):
            return await call_next(request)

        # Check credentials exist
        oauth = OAuthService()
        creds = oauth.get_credentials()
        if not creds:
            logger.warning({"action": "auth_middleware", "path": path, "status": "unauthenticated"})
            raise HTTPException(
                status_code=401,
                detail="Not authenticated. Visit /auth/login to connect your Google account.",
            )

        return await call_next(request)
