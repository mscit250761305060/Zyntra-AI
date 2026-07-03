"""Service layer for session management."""
import logging
from typing import Optional, List, Dict, Any
from uuid import uuid4
from datetime import datetime
from src.repositories.session_repository import session_repository
from src.repositories.message_repository import message_repository
from src.agents.sessions.session_manager import session_manager
from src.core.config import settings

logger = logging.getLogger("zyntra.session_service")


class SessionService:
    """Business logic layer for session operations."""

    async def create_session(
        self,
        user_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new session."""
        try:
            if not session_id:
                session_id = str(uuid4())

            # Create in ADK and MySQL
            await session_manager.create_session(
                session_id=session_id,
                user_id=user_id,
                title=title,
                description=description,
                app_name="zyntra",
            )

            session_data = session_repository.get_session(session_id)
            logger.info(f"Session created successfully: {session_id}")

            return {
                "session_id": session_id,
                "user_id": user_id,
                "title": title,
                "description": description,
                "created_at": session_data["created_at"],
                "is_active": session_data["is_active"],
            }

        except Exception as err:
            logger.error(f"Error creating session: {err}")
            raise

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session details."""
        try:
            session_data = session_repository.get_session(session_id)
            if not session_data:
                logger.warning(f"Session not found: {session_id}")
                return None

            # Get message count
            message_count = message_repository.get_session_message_count(session_id)

            result = {
                "session_id": session_data["session_id"],
                "user_id": session_data["user_id"],
                "title": session_data["title"],
                "description": session_data["description"],
                "app_name": session_data["app_name"],
                "created_at": session_data["created_at"],
                "updated_at": session_data["updated_at"],
                "last_accessed_at": session_data["last_accessed_at"],
                "is_active": session_data["is_active"],
                "is_pinned": session_data.get("is_pinned", False),
                "message_count": message_count,
            }

            return result

        except Exception as err:
            logger.error(f"Error retrieving session {session_id}: {err}")
            raise

    async def get_user_sessions(
        self, user_id: str, active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Get all sessions for a user."""
        try:
            sessions = session_repository.get_user_sessions(
                user_id=user_id, active_only=active_only
            )

            result = []
            for session in sessions:
                message_count = message_repository.get_session_message_count(
                    session["session_id"]
                )
                result.append(
                    {
                        "session_id": session["session_id"],
                        "user_id": session.get("user_id", user_id),
                        "title": session.get("title"),
                        "description": session.get("description"),
                        "app_name": session.get("app_name", "chatbot"),
                        "created_at": session.get("created_at", datetime.now().isoformat()),
                        "updated_at": session.get("updated_at", session.get("created_at", datetime.now().isoformat())),
                        "last_accessed_at": session.get("last_accessed_at"),
                        "is_active": session.get("is_active", True),
                        "is_pinned": session.get("is_pinned", False),
                        "message_count": message_count,
                    }
                )

            logger.info(f"Retrieved {len(result)} sessions for user {user_id}")
            return result

        except Exception as err:
            logger.error(f"Error retrieving sessions for user {user_id}: {err}")
            raise

    async def update_session(
        self,
        session_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        is_pinned: Optional[bool] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update session metadata."""
        try:
            await session_manager.update_session(
                session_id=session_id, title=title, description=description, is_pinned=is_pinned
            )

            session_data = await self.get_session(session_id)
            logger.info(f"Session {session_id} updated successfully")
            return session_data

        except Exception as err:
            logger.error(f"Error updating session {session_id}: {err}")
            raise

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session and all related data."""
        try:
            # Get session to verify it exists
            session_data = session_repository.get_session(session_id)
            if not session_data:
                logger.warning(f"Session not found: {session_id}")
                return False

            user_id = session_data["user_id"]

            # Delete from ADK and MySQL
            await session_manager.delete_session(
                session_id=session_id, user_id=user_id
            )

            logger.info(f"Session {session_id} deleted successfully")
            return True

        except Exception as err:
            logger.error(f"Error deleting session {session_id}: {err}")
            raise

    async def get_session_history(
        self, session_id: str, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get conversation history for a session."""
        try:
            messages = message_repository.get_session_messages(
                session_id=session_id, limit=limit, offset=offset
            )
            logger.info(f"Retrieved {len(messages)} messages for session {session_id}")
            return messages

        except Exception as err:
            logger.error(f"Error retrieving history for session {session_id}: {err}")
            raise

    async def clear_session_history(self, session_id: str) -> int:
        """Delete all messages in a session but keep the session."""
        try:
            count = message_repository.delete_session_messages(session_id)
            logger.info(f"Cleared {count} messages from session {session_id}")
            return count

        except Exception as err:
            logger.error(f"Error clearing history for session {session_id}: {err}")
            raise


# Global session service instance
session_service = SessionService()
