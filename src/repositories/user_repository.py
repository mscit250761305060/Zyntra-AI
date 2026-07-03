"""Database repository for user operations."""
import logging
from typing import Optional, List, Dict, Any
from uuid import uuid4
from src.persistence.file_persistence import file_persistence

logger = logging.getLogger("zyntra.user_repository")


class UserRepository:
    """Handles user-related operations using file-based persistence."""

    def create_user(
        self,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        email: Optional[str] = None,
        password_hash: Optional[str] = None,
        profile_image: Optional[str] = None,
        auth_provider: str = "local",
    ) -> str:
        """Create a new user."""
        try:
            if not user_id:
                user_id = str(uuid4())

            file_persistence.create_user(
                user_id, 
                username, 
                email, 
                password_hash, 
                profile_image, 
                auth_provider
            )
            logger.info(f"User created: {user_id}")
            return user_id
        except Exception as err:
            logger.error(f"Error creating user: {err}")
            raise

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a user by ID."""
        try:
            return file_persistence.get_user(user_id)
        except Exception as err:
            logger.error(f"Error retrieving user {user_id}: {err}")
            raise

    def user_exists(self, user_id: str) -> bool:
        """Check if a user exists."""
        try:
            user = self.get_user(user_id)
            return user is not None
        except Exception as err:
            logger.error(f"Error checking if user exists: {err}")
            raise

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Retrieve user by email."""
        try:
            return file_persistence.get_user_by_email(email)
        except Exception as err:
            logger.error(f"Error retrieving user by email {email}: {err}")
            raise

    def update_user_last_login(self, user_id: str):
        """Update last login."""
        try:
            file_persistence.update_user_last_login(user_id)
        except Exception as err:
            logger.error(f"Error updating last login for user {user_id}: {err}")
            raise

    def update_user(
        self,
        user_id: str,
        username: Optional[str] = None,
        email: Optional[str] = None,
        profile_image: Optional[str] = None,
    ) -> bool:
        """Update user information."""
        try:
            from src.persistence.file_persistence import USERS_FILE
            users = file_persistence._load_json(USERS_FILE)
            
            if user_id not in users:
                return False

            if username is not None:
                users[user_id]["username"] = username
            if email is not None:
                users[user_id]["email"] = email
            if profile_image is not None:
                users[user_id]["profile_image"] = profile_image

            file_persistence._save_json(USERS_FILE, users)
            logger.info(f"User {user_id} updated")
            return True

        except Exception as err:
            logger.error(f"Error updating user {user_id}: {err}")
            raise

    def delete_user(self, user_id: str) -> bool:
        """Delete a user and all their related data."""
        try:
            from src.persistence.file_persistence import USERS_FILE
            users = file_persistence._load_json(USERS_FILE)
            
            if user_id not in users:
                return False

            del users[user_id]
            file_persistence._save_json(USERS_FILE, users)
            logger.info(f"User {user_id} deleted")
            return True
        except Exception as err:
            logger.error(f"Error deleting user {user_id}: {err}")
            raise

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Retrieve all users."""
        try:
            from src.persistence.file_persistence import USERS_FILE
            users = file_persistence._load_json(USERS_FILE)
            return list(users.values())
        except Exception as err:
            logger.error(f"Error retrieving all users: {err}")
            raise


# Global user repository instance
user_repository = UserRepository()
