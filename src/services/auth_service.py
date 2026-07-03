import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from src.core.security import (
    verify_password, get_password_hash,
    create_access_token, create_refresh_token,
    decode_refresh_token, REFRESH_TOKEN_EXPIRE_DAYS
)
from src.repositories.user_repository import user_repository
from src.persistence.file_persistence import file_persistence

logger = logging.getLogger("zyntra.auth_service")

class AuthService:
    def __init__(self):
        pass

    def register_user(self, name: str, email: str, password: str) -> str:
        """Register a new user with email and password."""
        existing_user = user_repository.get_user_by_email(email)
        if existing_user:
            raise ValueError("Email already registered")

        hashed_password = get_password_hash(password)
        
        user_id = str(uuid.uuid4())
        user_repository.create_user(
            user_id=user_id,
            username=name,
            email=email,
            password_hash=hashed_password,
            auth_provider="local"
        )
        return user_id

    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user by email and password, returning tokens."""
        user = user_repository.get_user_by_email(email)
        if not user:
            raise ValueError("Invalid email or password")
            
        if user.get("auth_provider") != "local":
            raise ValueError(f"Please login using {user.get('auth_provider')}")

        if not verify_password(password, user.get("password_hash", "")):
            raise ValueError("Invalid email or password")

        user_repository.update_user_last_login(user["user_id"])
        
        return self._generate_tokens(user["user_id"], user["username"], user["email"])

    def authenticate_google(self, email: str, name: str, profile_image: str = None) -> Dict[str, Any]:
        """Authenticate user via Google (register if new)."""
        user = user_repository.get_user_by_email(email)
        
        if not user:
            # Auto-register new Google user
            user_id = str(uuid.uuid4())
            user_repository.create_user(
                user_id=user_id,
                username=name,
                email=email,
                profile_image=profile_image,
                auth_provider="google"
            )
            user = user_repository.get_user(user_id)
        
        else:
            # Save the authenticated user's data to the database after successful login
            user_repository.update_user(
                user_id=user["user_id"],
                username=name,
                profile_image=profile_image
            )
            user["username"] = name
            user["profile_image"] = profile_image
        
        # Even if they signed up locally, allow Google login if email matches
        # or maybe we restrict it. For now, allow it to just return tokens.
        user_repository.update_user_last_login(user["user_id"])
        
        return self._generate_tokens(user["user_id"], user["username"], user["email"])

    def _generate_tokens(self, user_id: str, name: str, email: str) -> Dict[str, Any]:
        """Generate access and refresh tokens."""
        access_token = create_access_token(subject=user_id)
        refresh_token = create_refresh_token(subject=user_id)
        
        expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        file_persistence.save_refresh_token(refresh_token, user_id, expires_at)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_id": user_id,
            "name": name,
            "email": email
        }

    def refresh_tokens(self, refresh_token: str) -> Dict[str, Any]:
        """Use a refresh token to get a new access token."""
        token_record = file_persistence.get_refresh_token(refresh_token)
        if not token_record or token_record.get("revoked"):
            raise ValueError("Invalid or revoked refresh token")
            
        try:
            payload = decode_refresh_token(refresh_token)
            user_id = payload.get("sub")
            if not user_id or user_id != token_record["user_id"]:
                raise ValueError("Invalid token subject")
                
            user = user_repository.get_user(user_id)
            if not user:
                raise ValueError("User not found")
                
            # Optionally revoke old refresh token and generate new one
            file_persistence.revoke_refresh_token(refresh_token)
            
            return self._generate_tokens(user["user_id"], user["username"], user["email"])
        except Exception as e:
            raise ValueError(f"Token validation failed: {str(e)}")

    def logout(self, refresh_token: str):
        """Logout user by revoking refresh token."""
        if refresh_token:
            file_persistence.revoke_refresh_token(refresh_token)

auth_service = AuthService()
