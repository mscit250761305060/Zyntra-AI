import logging
from typing import Optional, List, Dict, Any
from src.repositories.session_repository import session_repository

logger = logging.getLogger("zyntra.user_session")

class UserSession:
    """Handles database persistence for user-specific sessions and metadata."""

    async def create_db_session(self, session_id: str, app_name: str, user_id: str, title: Optional[str] = None, description: Optional[str] = None) -> str:
        try:
            db_session_id = session_repository.create_session(
                user_id=user_id, session_id=session_id, app_name=app_name, title=title, description=description
            )
            logger.info(f"Session persisted to database: {db_session_id}")
            return db_session_id
        except Exception as e:
            logger.error(f"Error persisting session {session_id} to DB: {e}")
            raise

    async def delete_db_session(self, session_id: str):
        try:
            session_repository.delete_session(session_id)
            logger.info(f"Session deleted from DB: {session_id}")
        except Exception as e:
            logger.error(f"Error deleting DB session {session_id}: {e}")
            raise

    async def get_user_sessions(self, user_id: str, app_name: str = "chatbot") -> List[Dict[str, Any]]:
        try:
            sessions = session_repository.get_user_sessions(user_id, app_name)
            logger.info(f"Retrieved {len(sessions)} sessions for user {user_id}")
            return sessions
        except Exception as e:
            logger.error(f"Error retrieving user sessions for {user_id}: {e}")
            raise

    async def update_session(self, session_id: str, title: Optional[str] = None, description: Optional[str] = None, is_active: Optional[bool] = None, is_pinned: Optional[bool] = None) -> bool:
        try:
            success = session_repository.update_session(
                session_id=session_id, title=title, description=description, is_active=is_active, is_pinned=is_pinned
            )
            logger.info(f"Session {session_id} updated: {success}")
            return success
        except Exception as e:
            logger.error(f"Error updating session {session_id}: {e}")
            raise
