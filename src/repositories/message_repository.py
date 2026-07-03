"""Database repository for message operations."""
import logging
from typing import Optional, List, Dict, Any
from uuid import uuid4
from datetime import datetime
from src.persistence.file_persistence import file_persistence

logger = logging.getLogger("zyntra.message_repository")


class MessageRepository:
    """Handles message-related operations using file-based persistence."""

    def create_message(
        self,
        session_id: str,
        user_id: str,
        role: str,
        content: str,
        message_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        message_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a new message."""
        try:
            if not message_id:
                message_id = str(uuid4())

            message_id = file_persistence.create_message(
                session_id=session_id,
                user_id=user_id,
                role=role,
                content=content,
                agent_name=agent_name,
            )

            logger.info(
                f"Message created: {message_id} in session: {session_id}, role: {role}"
            )
            return message_id

        except Exception as err:
            logger.error(f"Error creating message: {err}")
            raise

    def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a message by ID."""
        try:
            from src.persistence.file_persistence import MESSAGES_FILE
            messages_data = file_persistence._load_json(MESSAGES_FILE)
            
            for session_messages in messages_data.values():
                for msg in session_messages:
                    if msg.get("message_id") == message_id:
                        return msg
            return None
        except Exception as err:
            logger.error(f"Error retrieving message {message_id}: {err}")
            raise

    def get_session_messages(
        self, session_id: str, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Retrieve messages from a session."""
        try:
            messages = file_persistence.get_session_messages(session_id)
            return messages[offset:offset + limit]
        except Exception as err:
            logger.error(f"Error retrieving messages for session {session_id}: {err}")
            raise

    def get_session_message_count(self, session_id: str) -> int:
        """Get the total number of messages in a session."""
        try:
            messages = file_persistence.get_session_messages(session_id)
            return len(messages)
        except Exception as err:
            logger.error(f"Error counting messages for session {session_id}: {err}")
            raise

    def get_user_messages(
        self, user_id: str, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Retrieve messages from a user across all sessions."""
        try:
            from src.repositories.session_repository import session_repository
            sessions = session_repository.get_user_sessions(user_id)
            
            all_messages = []
            for session in sessions:
                messages = self.get_session_messages(session["session_id"])
                all_messages.extend(messages)
            
            # Sort by created_at descending and apply pagination
            all_messages.sort(
                key=lambda m: m.get("created_at", ""),
                reverse=True
            )
            return all_messages[offset:offset + limit]

        except Exception as err:
            logger.error(f"Error retrieving messages for user {user_id}: {err}")
            raise

    def search_messages(self, user_id: str, query: str) -> List[str]:
        """Search for a query in all user messages and return matching session IDs."""
        try:
            from src.repositories.session_repository import session_repository
            sessions = session_repository.get_user_sessions(user_id)
            session_ids = {s["session_id"] for s in sessions}
            
            from src.persistence.file_persistence import MESSAGES_FILE
            messages_data = file_persistence._load_json(MESSAGES_FILE)
            
            matching_session_ids = set()
            query_lower = query.lower()
            
            for session_id, session_messages in messages_data.items():
                if session_id in session_ids:
                    for msg in session_messages:
                        if msg.get("content") and query_lower in msg.get("content").lower():
                            matching_session_ids.add(session_id)
                            break
                            
            return list(matching_session_ids)
        except Exception as err:
            logger.error(f"Error searching messages for user {user_id}: {err}")
            raise

    def delete_message(self, message_id: str) -> bool:
        """Delete a message."""
        try:
            from src.persistence.file_persistence import MESSAGES_FILE
            messages_data = file_persistence._load_json(MESSAGES_FILE)
            
            for session_id, session_messages in list(messages_data.items()):
                messages_data[session_id] = [
                    msg for msg in session_messages if msg.get("message_id") != message_id
                ]
                if not messages_data[session_id]:
                    del messages_data[session_id]
            
            file_persistence._save_json(MESSAGES_FILE, messages_data)
            logger.info(f"Message {message_id} deleted")
            return True
        except Exception as err:
            logger.error(f"Error deleting message {message_id}: {err}")
            raise

    def delete_session_messages(self, session_id: str) -> int:
        """Delete all messages in a session."""
        try:
            count = file_persistence.delete_session_messages(session_id)
            logger.info(f"Messages deleted for session {session_id}, count: {count}")
            return count
        except Exception as err:
            logger.error(f"Error deleting messages for session {session_id}: {err}")
            raise


# Global message repository instance
message_repository = MessageRepository()
