"""MySQL-based persistence for sessions, messages, and users."""
import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import uuid4
from src.core.database import db_manager

logger = logging.getLogger("zyntra.mysql_persistence")


class MySQLPersistence:
    """MySQL-based persistence system."""

    def __init__(self):
        pass

    # User Operations
    def create_user(
        self, 
        user_id: str, 
        username: Optional[str] = None, 
        email: Optional[str] = None,
        password_hash: Optional[str] = None,
        profile_image: Optional[str] = None,
        auth_provider: str = "local"
    ) -> str:
        """Create a user."""
        query = """
            INSERT INTO users (user_id, username, email, password_hash, profile_image, auth_provider)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                username = VALUES(username),
                email = VALUES(email),
                profile_image = VALUES(profile_image),
                auth_provider = VALUES(auth_provider)
        """
        params = (user_id, username, email, password_hash, profile_image, auth_provider)
        db_manager.execute_insert(query, params)
        logger.info(f"User created: {user_id}")
        return user_id

    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID."""
        query = "SELECT * FROM users WHERE user_id = %s"
        results = db_manager.execute_query(query, (user_id,))
        if results:
            # Convert datetime to string for compatibility
            user = results[0]
            if user.get("created_at"):
                user["created_at"] = user["created_at"].isoformat()
            if user.get("last_login"):
                user["last_login"] = user["last_login"].isoformat()
            if user.get("updated_at"):
                user["updated_at"] = user["updated_at"].isoformat()
            return user
        return None

    def user_exists(self, user_id: str) -> bool:
        """Check if user exists."""
        return self.get_user(user_id) is not None

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email."""
        query = "SELECT * FROM users WHERE email = %s"
        results = db_manager.execute_query(query, (email,))
        if results:
            user = results[0]
            if user.get("created_at"):
                user["created_at"] = user["created_at"].isoformat()
            if user.get("last_login"):
                user["last_login"] = user["last_login"].isoformat()
            if user.get("updated_at"):
                user["updated_at"] = user["updated_at"].isoformat()
            return user
        return None

    def update_user(self, user_id: str, username: Optional[str] = None, email: Optional[str] = None, profile_image: Optional[str] = None) -> bool:
        """Update user information."""
        updates = []
        params = []
        if username is not None:
            updates.append("username = %s")
            params.append(username)
        if email is not None:
            updates.append("email = %s")
            params.append(email)
        if profile_image is not None:
            updates.append("profile_image = %s")
            params.append(profile_image)
            
        if not updates:
            return False
            
        query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = %s"
        params.append(user_id)
        affected = db_manager.execute_update(query, tuple(params))
        return affected > 0

    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        query = "DELETE FROM users WHERE user_id = %s"
        affected = db_manager.execute_delete(query, (user_id,))
        return affected > 0

    def get_all_users(self) -> List[Dict]:
        """Get all users."""
        query = "SELECT * FROM users"
        results = db_manager.execute_query(query)
        for user in results:
            if user.get("created_at"):
                user["created_at"] = user["created_at"].isoformat()
            if user.get("last_login"):
                user["last_login"] = user["last_login"].isoformat()
            if user.get("updated_at"):
                user["updated_at"] = user["updated_at"].isoformat()
        return results

    def update_user_last_login(self, user_id: str):
        """Update the last login timestamp for a user."""
        query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = %s"
        db_manager.execute_update(query, (user_id,))

    def save_refresh_token(self, token: str, user_id: str, expires_at: datetime):
        """Save a refresh token."""
        query = """
            INSERT INTO refresh_tokens (token, user_id, expires_at)
            VALUES (%s, %s, %s)
        """
        db_manager.execute_insert(query, (token, user_id, expires_at))

    def get_refresh_token(self, token: str) -> Optional[Dict]:
        query = "SELECT * FROM refresh_tokens WHERE token = %s"
        results = db_manager.execute_query(query, (token,))
        if results:
            rt = results[0]
            if rt.get("expires_at"):
                rt["expires_at"] = rt["expires_at"].isoformat()
            if rt.get("created_at"):
                rt["created_at"] = rt["created_at"].isoformat()
            # return format that matches file_persistence
            rt["revoked"] = bool(rt.get("revoked", 0))
            return rt
        return None

    def revoke_refresh_token(self, token: str):
        query = "UPDATE refresh_tokens SET revoked = TRUE WHERE token = %s"
        db_manager.execute_update(query, (token,))

    # Session Operations
    def create_session(self, user_id: str, session_id: Optional[str] = None, title: Optional[str] = None, description: Optional[str] = None, app_name: str = "chatbot") -> str:
        """Create a session."""
        if not session_id:
            session_id = str(uuid4())

        # Create user if doesn't exist
        if not self.user_exists(user_id):
            self.create_user(user_id)

        query = """
            INSERT INTO sessions (session_id, user_id, app_name, title, description)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                title = VALUES(title),
                description = VALUES(description),
                last_accessed_at = CURRENT_TIMESTAMP
        """
        params = (session_id, user_id, app_name, title or f"Session {session_id[:8]}", description)
        db_manager.execute_insert(query, params)
        logger.info(f"Session created: {session_id}")
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID."""
        query = "SELECT * FROM sessions WHERE session_id = %s"
        results = db_manager.execute_query(query, (session_id,))
        if results:
            session = results[0]
            if session.get("created_at"):
                session["created_at"] = session["created_at"].isoformat()
            if session.get("updated_at"):
                session["updated_at"] = session["updated_at"].isoformat()
            if session.get("last_accessed_at"):
                session["last_accessed_at"] = session["last_accessed_at"].isoformat()
            session["is_active"] = bool(session.get("is_active", 1))
            return session
        return None

    def get_user_sessions(self, user_id: str) -> List[Dict]:
        """Get all sessions for a user."""
        query = "SELECT * FROM sessions WHERE user_id = %s ORDER BY last_accessed_at DESC"
        results = db_manager.execute_query(query, (user_id,))
        
        for session in results:
            if session.get("created_at"):
                session["created_at"] = session["created_at"].isoformat()
            if session.get("updated_at"):
                session["updated_at"] = session["updated_at"].isoformat()
            if session.get("last_accessed_at"):
                session["last_accessed_at"] = session["last_accessed_at"].isoformat()
            session["is_active"] = bool(session.get("is_active", 1))
        return results

    def update_session(self, session_id: str, title: Optional[str] = None, description: Optional[str] = None, is_active: Optional[bool] = None) -> bool:
        """Update session information."""
        updates = []
        params = []
        if title is not None:
            updates.append("title = %s")
            params.append(title)
        if description is not None:
            updates.append("description = %s")
            params.append(description)
        if is_active is not None:
            updates.append("is_active = %s")
            params.append(is_active)
            
        if not updates:
            return False
            
        query = f"UPDATE sessions SET {', '.join(updates)} WHERE session_id = %s"
        params.append(session_id)
        affected = db_manager.execute_update(query, tuple(params))
        return affected > 0

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        query = "DELETE FROM sessions WHERE session_id = %s"
        affected = db_manager.execute_delete(query, (session_id,))
        if affected > 0:
            logger.info(f"Session deleted: {session_id}")
            return True
        return False

    # Message Operations
    def create_message(
        self,
        session_id: str,
        user_id: str,
        role: str,
        content: str,
        agent_name: Optional[str] = None,
    ) -> str:
        """Create a message."""
        message_id = str(uuid4())
        
        query = """
            INSERT INTO messages (session_id, user_id, message_id, role, content, agent_name)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (session_id, user_id, message_id, role, content, agent_name)
        db_manager.execute_insert(query, params)

        # Update session last accessed
        update_query = "UPDATE sessions SET last_accessed_at = CURRENT_TIMESTAMP WHERE session_id = %s"
        db_manager.execute_update(update_query, (session_id,))

        logger.info(f"Message created: {message_id}")
        return message_id

    def get_session_messages(self, session_id: str) -> List[Dict]:
        """Get messages from a session."""
        query = "SELECT * FROM messages WHERE session_id = %s ORDER BY created_at ASC"
        results = db_manager.execute_query(query, (session_id,))
        
        for msg in results:
            if msg.get("created_at"):
                msg["created_at"] = msg["created_at"].isoformat()
            if msg.get("updated_at"):
                msg["updated_at"] = msg["updated_at"].isoformat()
            if msg.get("metadata") and isinstance(msg["metadata"], str):
                try:
                    msg["metadata"] = json.loads(msg["metadata"])
                except json.JSONDecodeError:
                    pass
        return results

    def delete_session_messages(self, session_id: str) -> int:
        """Delete all messages in a session."""
        query = "DELETE FROM messages WHERE session_id = %s"
        affected = db_manager.execute_delete(query, (session_id,))
        return affected

    def get_message(self, message_id: str) -> Optional[Dict]:
        query = "SELECT * FROM messages WHERE message_id = %s"
        results = db_manager.execute_query(query, (message_id,))
        if results:
            msg = results[0]
            if msg.get("created_at"):
                msg["created_at"] = msg["created_at"].isoformat()
            if msg.get("updated_at"):
                msg["updated_at"] = msg["updated_at"].isoformat()
            if msg.get("metadata") and isinstance(msg["metadata"], str):
                try:
                    msg["metadata"] = json.loads(msg["metadata"])
                except json.JSONDecodeError:
                    pass
            return msg
        return None

    def get_user_messages(self, user_id: str) -> List[Dict]:
        query = "SELECT * FROM messages WHERE user_id = %s ORDER BY created_at DESC"
        results = db_manager.execute_query(query, (user_id,))
        for msg in results:
            if msg.get("created_at"):
                msg["created_at"] = msg["created_at"].isoformat()
            if msg.get("updated_at"):
                msg["updated_at"] = msg["updated_at"].isoformat()
            if msg.get("metadata") and isinstance(msg["metadata"], str):
                try:
                    msg["metadata"] = json.loads(msg["metadata"])
                except json.JSONDecodeError:
                    pass
        return results

    def delete_message(self, message_id: str) -> bool:
        query = "DELETE FROM messages WHERE message_id = %s"
        affected = db_manager.execute_delete(query, (message_id,))
        return affected > 0


# Global instance
mysql_persistence = MySQLPersistence()
