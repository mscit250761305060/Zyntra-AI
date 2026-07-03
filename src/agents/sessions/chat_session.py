import logging
from typing import Optional, List, Dict, Any
from src.repositories.message_repository import message_repository
from src.agents.sessions.memory_session import MemorySession

logger = logging.getLogger("zyntra.chat_session")

class ChatSession:
    """Handles conversation history and message persistence logic."""

    def __init__(self, memory_session: MemorySession):
        self.memory = memory_session

    async def get_history(self, session_id: str, app_name: str = "chatbot", user_id: str = "default_user") -> List[Dict[str, Any]]:
        """
        Retrieves conversation history prioritizing ADK in-memory history,
        falling back to database persistence.
        """
        try:
            session = await self.memory.get(session_id, app_name, user_id)
            history = []

            # Load from Memory First
            if session and session.events:
                for event in session.events:
                    if event.content and event.content.parts:
                        text_content = "".join([part.text for part in event.content.parts if part.text])
                        if text_content:
                            history.append({
                                "role": event.author,
                                "content": text_content,
                                "timestamp": event.timestamp,
                            })

            # Load from DB if memory is empty
            if not history:
                db_messages = message_repository.get_session_messages(session_id)
                for msg in db_messages:
                    history.append({
                        "role": msg["role"],
                        "content": msg["content"],
                        "timestamp": msg["created_at"],
                    })

            logger.info(f"Retrieved {len(history)} messages for session {session_id}")
            return history
        except Exception as e:
            logger.error(f"Error retrieving history for session {session_id}: {e}")
            return []

    async def persist_message(self, session_id: str, user_id: str, role: str, content: str, agent_name: Optional[str] = None, message_type: str = "text") -> str:
        """Persists a new message to the database."""
        try:
            message_id = message_repository.create_message(
                session_id=session_id, user_id=user_id, role=role, content=content, agent_name=agent_name, message_type=message_type
            )
            logger.info(f"Message persisted: {message_id}")
            return message_id
        except Exception as e:
            logger.error(f"Error persisting message: {e}")
            raise
