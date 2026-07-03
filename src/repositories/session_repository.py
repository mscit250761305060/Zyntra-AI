"""Database repository for session operations."""
import logging
from typing import Optional, List, Dict, Any
from uuid import uuid4
from datetime import datetime
from src.persistence.file_persistence import file_persistence

logger = logging.getLogger("zyntra.session_repository")


class SessionRepository:
    """Handles session-related operations using file-based persistence."""

    def create_session(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        app_name: str = "chatbot",
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> str:
        """Create a new session."""
        try:
            if not session_id:
                session_id = str(uuid4())

            # Use file persistence
            file_persistence.create_session(user_id, session_id, title)
            logger.info(f"Session created: {session_id} for user: {user_id}")
            return session_id

        except Exception as err:
            logger.error(f"Error creating session: {err}")
            raise

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a session by ID."""
        try:
            session = file_persistence.get_session(session_id)
            return session
        except Exception as err:
            logger.error(f"Error retrieving session {session_id}: {err}")
            raise

    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists."""
        try:
            session = self.get_session(session_id)
            return session is not None
        except Exception as err:
            logger.error(f"Error checking if session exists: {err}")
            raise

    def get_user_sessions(
        self, user_id: str, app_name: str = "chatbot", active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Retrieve all sessions for a user."""
        try:
            sessions = file_persistence.get_user_sessions(user_id)
            return sessions
        except Exception as err:
            logger.error(f"Error retrieving sessions for user {user_id}: {err}")
            raise

    def update_session(
        self,
        session_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_pinned: Optional[bool] = None,
    ) -> bool:
        """Update session information."""
        try:
            session = file_persistence.get_session(session_id)
            if not session:
                return False

            if title:
                session["title"] = title
            if description is not None:
                session["description"] = description
            if is_active is not None:
                session["is_active"] = is_active
            if is_pinned is not None:
                session["is_pinned"] = is_pinned

            # Save back
            from src.persistence.file_persistence import SESSIONS_FILE, file_persistence as fp
            sessions = fp._load_json(SESSIONS_FILE)
            sessions[session_id] = session
            fp._save_json(SESSIONS_FILE, sessions)

            logger.info(f"Session {session_id} updated")
            return True

        except Exception as err:
            logger.error(f"Error updating session {session_id}: {err}")
            raise

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all related data."""
        try:
            result = file_persistence.delete_session(session_id)
            logger.info(f"Session {session_id} deleted")
            return result
        except Exception as err:
            logger.error(f"Error deleting session {session_id}: {err}")
            raise


# Global session repository instance
session_repository = SessionRepository()
