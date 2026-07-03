import logging
from typing import Optional, List, Dict, Any
from google.adk.sessions.session import Session
from src.agents.sessions.memory_session import MemorySession
from src.agents.sessions.user_session import UserSession
from src.agents.sessions.chat_session import ChatSession

logger = logging.getLogger("zyntra.session_manager")

class SessionManager:
    """
    Facade for managing chatbot sessions. Coordinates interactions between:
    - ADK InMemorySessionService (via MemorySession)
    - Database persistence for sessions (via UserSession)
    - Chat history and messages (via ChatSession)
    """

    def __init__(self):
        self.memory_session = MemorySession()
        self.user_session = UserSession()
        self.chat_session = ChatSession(self.memory_session)
        # Expose the underlying InMemorySessionService so adk runners can use it
        self.session_service = self.memory_session.service

    async def get_session(self, session_id: str, app_name: str = "chatbot", user_id: str = "default_user") -> Optional[Session]:
        """Retrieves an existing session from the ADK session service."""
        return await self.memory_session.get(session_id, app_name, user_id)

    async def create_session(self, session_id: str, app_name: str = "chatbot", user_id: str = "default_user", state: Optional[Dict[str, Any]] = None, title: Optional[str] = None, description: Optional[str] = None) -> Optional[Session]:
        """Creates and registers a new session in both DB and memory."""
        await self.user_session.create_db_session(session_id, app_name, user_id, title, description)
        return await self.memory_session.create(session_id, app_name, user_id, state)

    async def delete_session(self, session_id: str, app_name: str = "chatbot", user_id: str = "default_user") -> None:
        """Deletes a session from both DB and memory."""
        await self.memory_session.delete(session_id, app_name, user_id)
        await self.user_session.delete_db_session(session_id)

    async def get_history(self, session_id: str, app_name: str = "chatbot", user_id: str = "default_user") -> List[Dict[str, Any]]:
        """Retrieves conversation history."""
        return await self.chat_session.get_history(session_id, app_name, user_id)

    async def persist_message(self, session_id: str, user_id: str, role: str, content: str, agent_name: Optional[str] = None, message_type: str = "text") -> str:
        """Persist a message for long-term storage."""
        return await self.chat_session.persist_message(session_id, user_id, role, content, agent_name, message_type)

    async def get_user_sessions(self, user_id: str, app_name: str = "chatbot") -> List[Dict[str, Any]]:
        """Get all sessions for a specific user."""
        return await self.user_session.get_user_sessions(user_id, app_name)

    async def update_session(self, session_id: str, title: Optional[str] = None, description: Optional[str] = None, is_active: Optional[bool] = None, is_pinned: Optional[bool] = None) -> bool:
        """Update session metadata in DB."""
        return await self.user_session.update_session(session_id, title, description, is_active, is_pinned)

# Global singleton instance
session_manager = SessionManager()