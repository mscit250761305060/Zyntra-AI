import logging
from typing import Optional, Dict, Any
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.sessions.session import Session

logger = logging.getLogger("zyntra.memory_session")

class MemorySession:
    """Handles the ADK InMemorySessionService for runtime session state."""

    def __init__(self):
        self.service = InMemorySessionService()

    async def get(self, session_id: str, app_name: str, user_id: str) -> Optional[Session]:
        try:
            return await self.service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
        except Exception as e:
            logger.error(f"Error retrieving memory session {session_id}: {e}")
            return None

    async def create(self, session_id: str, app_name: str, user_id: str, state: Optional[Dict[str, Any]] = None) -> Optional[Session]:
        try:
            session = await self.service.create_session(app_name=app_name, user_id=user_id, session_id=session_id, state=state)
            logger.info(f"Session created in ADK: {session_id}")
            return session
        except Exception as e:
            logger.error(f"Error creating memory session {session_id}: {e}")
            raise

    async def delete(self, session_id: str, app_name: str, user_id: str):
        try:
            await self.service.delete_session(app_name=app_name, user_id=user_id, session_id=session_id)
            logger.info(f"Session deleted from ADK: {session_id}")
        except Exception as e:
            logger.error(f"Error deleting memory session {session_id}: {e}")
            raise
