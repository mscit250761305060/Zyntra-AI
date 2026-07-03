"""Database models and schema definitions for the chatbot."""
from datetime import datetime
from typing import Optional


# SQL Table Creation Queries
USERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    profile_image VARCHAR(500),
    auth_provider VARCHAR(50) DEFAULT 'local',
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

SESSIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    app_name VARCHAR(100) DEFAULT 'chatbot',
    title VARCHAR(500),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_session_id (session_id),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

MESSAGES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    message_id VARCHAR(255) UNIQUE,
    role VARCHAR(50) NOT NULL COMMENT 'user, assistant, system',
    content LONGTEXT NOT NULL,
    agent_name VARCHAR(100),
    message_type VARCHAR(50) DEFAULT 'text' COMMENT 'text, tool_call, tool_response',
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_session_id (session_id),
    INDEX idx_user_id (user_id),
    INDEX idx_role (role),
    INDEX idx_created_at (created_at),
    INDEX idx_agent_name (agent_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

CONVERSATION_METADATA_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS conversation_metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    total_messages INT DEFAULT 0,
    total_user_messages INT DEFAULT 0,
    total_assistant_messages INT DEFAULT 0,
    first_message_at TIMESTAMP,
    last_message_at TIMESTAMP,
    conversation_duration_seconds INT,
    tags JSON,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_session_id (session_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

AGENT_INTERACTIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS agent_interactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    agent_name VARCHAR(100) NOT NULL,
    interaction_type VARCHAR(50) COMMENT 'call, response, tool_use',
    request_data JSON,
    response_data JSON,
    execution_time_ms INT,
    status VARCHAR(50) COMMENT 'success, error, timeout',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_session_id (session_id),
    INDEX idx_user_id (user_id),
    INDEX idx_agent_name (agent_name),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

AUDIT_LOG_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    details JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    status VARCHAR(50) COMMENT 'success, error',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id),
    INDEX idx_action (action),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

REFRESH_TOKENS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    token VARCHAR(500) UNIQUE NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_token (token)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

# Python Models for Type Hints
class User:
    """User model."""

    def __init__(
        self,
        user_id: str,
        username: Optional[str] = None,
        email: Optional[str] = None,
        password_hash: Optional[str] = None,
        profile_image: Optional[str] = None,
        auth_provider: str = "local",
        last_login: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
    ):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.profile_image = profile_image
        self.auth_provider = auth_provider
        self.last_login = last_login
        self.created_at = created_at or datetime.now()


class Session:
    """Session model."""

    def __init__(
        self,
        session_id: str,
        user_id: str,
        app_name: str = "chatbot",
        title: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        self.session_id = session_id
        self.user_id = user_id
        self.app_name = app_name
        self.title = title
        self.created_at = created_at or datetime.now()
        self.is_active = True


class Message:
    """Message model."""

    def __init__(
        self,
        session_id: str,
        user_id: str,
        role: str,
        content: str,
        message_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        message_type: str = "text",
        created_at: Optional[datetime] = None,
    ):
        self.session_id = session_id
        self.user_id = user_id
        self.message_id = message_id
        self.role = role
        self.content = content
        self.agent_name = agent_name
        self.message_type = message_type
        self.created_at = created_at or datetime.now()
