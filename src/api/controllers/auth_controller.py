import logging
from typing import Any
from fastapi import HTTPException, Response

from src.models.schemas import UserSignupRequest, UserLoginRequest, GoogleLoginRequest, TokenResponse, UserProfileResponse
from src.services.auth_service import auth_service

logger = logging.getLogger("zyntra.auth_controller")

class AuthController:
    """Controller for authentication operations."""

    async def register_user(self, request: UserSignupRequest, response: Response) -> TokenResponse:
        """Register a new user."""
        try:
            auth_service.register_user(request.name, request.email, request.password)
            # Auto login after signup
            tokens = auth_service.authenticate_user(request.email, request.password)
            self._set_auth_cookies(response, tokens)
            response.status_code = 201
            return TokenResponse(**tokens)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def login_user(self, request: UserLoginRequest, response: Response) -> TokenResponse:
        """Login an existing user."""
        try:
            tokens = auth_service.authenticate_user(request.email, request.password)
            self._set_auth_cookies(response, tokens)
            return TokenResponse(**tokens)
        except ValueError as e:
            raise HTTPException(status_code=401, detail=str(e))
        except Exception as e:
            logger.error(f"Error logging in user: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def google_login(self, request: GoogleLoginRequest, response: Response) -> TokenResponse:
        """Login or register via Google OAuth."""
        try:
            from google.oauth2 import id_token
            from google.auth.transport import requests
            from src.core.config import settings
            
            if not settings.GOOGLE_CLIENT_ID:
                logger.error("GOOGLE_CLIENT_ID is not configured in .env")
                raise ValueError("Google OAuth is not configured on the server.")

            try:
                # Verify the token with Google
                idinfo = id_token.verify_oauth2_token(
                    request.credential, 
                    requests.Request(), 
                    settings.GOOGLE_CLIENT_ID
                )
            except ValueError as e:
                logger.error(f"Invalid Google token: {e}")
                raise ValueError("Invalid Google token provided.")

            email = idinfo.get("email")
            name = idinfo.get("name")
            picture = idinfo.get("picture")
            
            if not email:
                raise ValueError("Google credential did not provide an email address.")

            tokens = auth_service.authenticate_google(email, name, picture)
            self._set_auth_cookies(response, tokens)
            return TokenResponse(**tokens)
        except ValueError as e:
            raise HTTPException(status_code=401, detail=str(e))
        except Exception as e:
            logger.error(f"Error during Google login: {e}")
            raise HTTPException(status_code=401, detail="Google authentication failed")

    async def refresh_tokens(self, request: dict, response: Response) -> TokenResponse:
        """Refresh access token using refresh token."""
        try:
            refresh_token = request.get("refresh_token")
            if not refresh_token:
                raise ValueError("Refresh token missing")
                
            tokens = auth_service.refresh_tokens(refresh_token)
            self._set_auth_cookies(response, tokens)
            return TokenResponse(**tokens)
        except ValueError as e:
            raise HTTPException(status_code=401, detail=str(e))
        except Exception as e:
            logger.error(f"Error refreshing tokens: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def logout_user(self, refresh_token: str, response: Response):
        """Logout user and clear cookies."""
        try:
            auth_service.logout(refresh_token)
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")
            return {"detail": "Successfully logged out"}
        except Exception as e:
            logger.error(f"Error logging out: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def _set_auth_cookies(self, response: Response, tokens: dict):
        """Set HTTP-only cookies for tokens."""
        from src.core.config import settings
        is_secure = settings.APP_ENV == "production"
        
        # HttpOnly prevents XSS, Secure ensures HTTPS
        response.set_cookie(
            key="access_token",
            value=tokens["access_token"],
            httponly=True,
            secure=is_secure,
            samesite="lax",
            max_age=30 * 60 # 30 minutes
        )
        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh_token"],
            httponly=True,
            secure=is_secure,
            samesite="lax",
            max_age=7 * 24 * 60 * 60 # 7 days
        )

auth_controller = AuthController()
