"""File-based persistence for sessions and messages (no MySQL required)."""
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import uuid4

logger = logging.getLogger("zyntra.file_persistence")

# Create data directory
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

SESSIONS_FILE = DATA_DIR / "sessions.json"
MESSAGES_FILE = DATA_DIR / "messages.json"
USERS_FILE = DATA_DIR / "users.json"


class FileBasedPersistence:
    """File-based persistence system - works without MySQL."""

    def __init__(self):
        self._ensure_files()

    def _ensure_files(self):
        """Create data files if they don't exist."""
        if not SESSIONS_FILE.exists():
            SESSIONS_FILE.write_text(json.dumps({}))
        if not MESSAGES_FILE.exists():
            MESSAGES_FILE.write_text(json.dumps({}))
        if not USERS_FILE.exists():
            USERS_FILE.write_text(json.dumps({}))

    def _load_json(self, filepath: Path) -> Dict:
        """Load JSON file."""
        try:
            return json.loads(filepath.read_text())
        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")
            return {}

    def _save_json(self, filepath: Path, data: Dict):
        """Save JSON file."""
        try:
            filepath.write_text(json.dumps(data, indent=2, default=str))
        except Exception as e:
            logger.error(f"Error saving {filepath}: {e}")
            raise

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
        users = self._load_json(USERS_FILE)
        if user_id not in users:
            users[user_id] = {
                "user_id": user_id,
                "username": username,
                "email": email,
                "password_hash": password_hash,
                "profile_image": profile_image,
                "auth_provider": auth_provider,
                "last_login": None,
                "created_at": datetime.now().isoformat(),
            }
            self._save_json(USERS_FILE, users)
            logger.info(f"User created: {user_id}")
        return user_id

    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID."""
        users = self._load_json(USERS_FILE)
        return users.get(user_id)

    def user_exists(self, user_id: str) -> bool:
        """Check if user exists."""
        return self.get_user(user_id) is not None

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email."""
        users = self._load_json(USERS_FILE)
        for u in users.values():
            if u.get("email") == email:
                return u
        return None

    def update_user_last_login(self, user_id: str):
        """Update the last login timestamp for a user."""
        users = self._load_json(USERS_FILE)
        if user_id in users:
            users[user_id]["last_login"] = datetime.now().isoformat()
            self._save_json(USERS_FILE, users)

    def save_refresh_token(self, token: str, user_id: str, expires_at: datetime):
        """Save a refresh token (using a dummy tokens.json file conceptually, but stored in SESSIONS_FILE as an extension for simplicity or separate)."""
        # We will use a separate file for refresh tokens
        TOKENS_FILE = DATA_DIR / "refresh_tokens.json"
        if not TOKENS_FILE.exists():
            TOKENS_FILE.write_text(json.dumps({}))
        tokens = self._load_json(TOKENS_FILE)
        tokens[token] = {
            "token": token,
            "user_id": user_id,
            "expires_at": expires_at.isoformat(),
            "created_at": datetime.now().isoformat(),
            "revoked": False
        }
        self._save_json(TOKENS_FILE, tokens)

    def get_refresh_token(self, token: str) -> Optional[Dict]:
        TOKENS_FILE = DATA_DIR / "refresh_tokens.json"
        if not TOKENS_FILE.exists():
            return None
        tokens = self._load_json(TOKENS_FILE)
        return tokens.get(token)

    def revoke_refresh_token(self, token: str):
        TOKENS_FILE = DATA_DIR / "refresh_tokens.json"
        if not TOKENS_FILE.exists():
            return
        tokens = self._load_json(TOKENS_FILE)
        if token in tokens:
            tokens[token]["revoked"] = True
            self._save_json(TOKENS_FILE, tokens)

    # Session Operations
    def create_session(self, user_id: str, session_id: Optional[str] = None, title: Optional[str] = None, description: Optional[str] = None, app_name: str = "chatbot") -> str:
        """Create a session."""
        if not session_id:
            session_id = str(uuid4())

        # Create user if doesn't exist
        if not self.user_exists(user_id):
            self.create_user(user_id)

        now = datetime.now().isoformat()
        sessions = self._load_json(SESSIONS_FILE)
        sessions[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "title": title or f"Session {session_id[:8]}",
            "description": description,
            "app_name": app_name,
            "created_at": now,
            "updated_at": now,
            "last_accessed_at": now,
            "is_active": True,
            "message_count": 0,
        }
        self._save_json(SESSIONS_FILE, sessions)
        logger.info(f"Session created: {session_id}")
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID."""
        sessions = self._load_json(SESSIONS_FILE)
        return sessions.get(session_id)

    def get_user_sessions(self, user_id: str) -> List[Dict]:
        """Get all sessions for a user."""
        sessions = self._load_json(SESSIONS_FILE)
        return [s for s in sessions.values() if s["user_id"] == user_id]

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        sessions = self._load_json(SESSIONS_FILE)
        if session_id in sessions:
            del sessions[session_id]
            self._save_json(SESSIONS_FILE, sessions)
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
        
        messages = self._load_json(MESSAGES_FILE)
        if session_id not in messages:
            messages[session_id] = []

        messages[session_id].append({
            "message_id": message_id,
            "session_id": session_id,
            "user_id": user_id,
            "role": role,
            "content": content,
            "agent_name": agent_name,
            "created_at": datetime.now().isoformat(),
        })

        self._save_json(MESSAGES_FILE, messages)

        # Update session message count
        sessions = self._load_json(SESSIONS_FILE)
        if session_id in sessions:
            sessions[session_id]["message_count"] = len(messages[session_id])
            self._save_json(SESSIONS_FILE, sessions)

        logger.info(f"Message created: {message_id}")
        return message_id

    def get_session_messages(self, session_id: str) -> List[Dict]:
        """Get messages from a session."""
        messages = self._load_json(MESSAGES_FILE)
        return messages.get(session_id, [])

    def delete_session_messages(self, session_id: str) -> int:
        """Delete all messages in a session."""
        messages = self._load_json(MESSAGES_FILE)
        count = len(messages.get(session_id, []))
        if session_id in messages:
            del messages[session_id]
            self._save_json(MESSAGES_FILE, messages)
        return count


# Global instance
file_persistence = FileBasedPersistence()
