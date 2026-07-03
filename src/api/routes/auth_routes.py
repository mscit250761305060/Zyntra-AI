import logging
from typing import Any
from fastapi import APIRouter, Depends, Request, Response

from src.models.schemas import UserSignupRequest, UserLoginRequest, GoogleLoginRequest, TokenResponse, UserProfileResponse, ErrorResponse
from src.api.controllers.auth_controller import auth_controller
from src.api.middleware.auth_middleware import get_current_user
from src.core.config import settings

logger = logging.getLogger("zyntra.auth_routes")

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@router.get("/config")
async def get_auth_config():
    """Get public auth configuration."""
    return {"google_client_id": settings.GOOGLE_CLIENT_ID}

@router.post("/signup", response_model=TokenResponse, responses={400: {"model": ErrorResponse}})
async def signup(request: UserSignupRequest, response: Response):
    """Register a new user account."""
    return await auth_controller.register_user(request, response)

@router.post("/login", response_model=TokenResponse, responses={401: {"model": ErrorResponse}})
async def login(request: UserLoginRequest, response: Response):
    """Login with email and password."""
    return await auth_controller.login_user(request, response)

@router.post("/google", response_model=TokenResponse, responses={401: {"model": ErrorResponse}})
async def google_login(request: GoogleLoginRequest, response: Response):
    """Login with Google credential."""
    return await auth_controller.google_login(request, response)

@router.post("/refresh", response_model=TokenResponse, responses={401: {"model": ErrorResponse}})
async def refresh_token(request: Request, response: Response):
    """Refresh access token."""
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        body = await request.json()
        refresh_token = body.get("refresh_token")
    return await auth_controller.refresh_tokens({"refresh_token": refresh_token}, response)

@router.post("/logout")
async def logout(request: Request, response: Response):
    """Logout and clear cookies."""
    refresh_token = request.cookies.get("refresh_token")
    return await auth_controller.logout_user(refresh_token, response)

@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get the current authenticated user's profile."""
    return UserProfileResponse(
        user_id=current_user["user_id"],
        name=current_user["username"],
        email=current_user["email"],
        profile_image=current_user.get("profile_image"),
        auth_provider=current_user.get("auth_provider", "local"),
        created_at=current_user["created_at"],
        last_login=current_user.get("last_login")
    )
