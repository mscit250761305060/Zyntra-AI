"""Pydantic models and schemas for API requests and responses."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


# Chat Schemas
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    session_id: Optional[str] = Field(None, description="Unique identifier for the chat session")
    chat_id: Optional[str] = Field(None, description="Alias for session_id (ChatGPT style)")
    message: str = Field(..., description="The message to send to the chatbot")
    user_id: Optional[str] = Field(None, description="User ID (optional, defaults to default_user)")

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")
        return v


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="The response from the chatbot")
    session_id: str = Field(..., description="The session ID")
    chat_id: Optional[str] = Field(None, description="Alias for session ID")


class ChatHistoryRequest(BaseModel):
    """Request model for chat history endpoint."""
    session_id: str = Field(..., description="Session ID")
    limit: int = Field(50, description="Max number of messages to retrieve")
    offset: int = Field(0, description="Offset for pagination")


class MessageModel(BaseModel):
    """Model for a single message."""
    id: Optional[int] = None
    message_id: Optional[str] = None
    session_id: str
    user_id: str
    role: str = Field(..., description="Role: user, assistant, chatbot")
    content: str
    agent_name: Optional[str] = None
    message_type: str = "text"
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ChatHistoryResponse(BaseModel):
    """Response model for chat history."""
    session_id: str
    chat_id: Optional[str] = None
    messages: List[MessageModel]
    count: int


class ChatHistoryItemResponse(BaseModel):
    """ChatGPT-style chat history list item."""
    chat_id: str
    title: Optional[str] = None
    last_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ChatListResponse(BaseModel):
    """ChatGPT-style chat list response."""
    chats: List[ChatHistoryItemResponse]


# Session Schemas
class SessionCreateRequest(BaseModel):
    """Request model for creating a session."""
    user_id: str = Field(..., description="User ID")
    title: Optional[str] = Field(None, description="Session title")
    description: Optional[str] = Field(None, description="Session description")
    session_id: Optional[str] = Field(None, description="Custom session ID (optional)")


class SessionUpdateRequest(BaseModel):
    """Request model for updating a session."""
    title: Optional[str] = Field(None, description="New session title")
    description: Optional[str] = Field(None, description="New session description")
    is_pinned: Optional[bool] = Field(None, description="Pin or unpin the session")


class SessionModel(BaseModel):
    """Model for session data."""
    session_id: str
    user_id: str
    app_name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_accessed_at: Optional[datetime] = None
    is_active: bool = True
    is_pinned: bool = False
    message_count: int = 0


class SessionCreateResponse(BaseModel):
    """Response model for creating a session."""
    session_id: str
    user_id: str
    title: Optional[str]
    description: Optional[str]
    created_at: datetime
    is_active: bool


class SessionDetailsResponse(BaseModel):
    """Response model for session details."""
    session_id: str
    user_id: str
    title: Optional[str]
    description: Optional[str]
    app_name: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_accessed_at: Optional[datetime]
    is_active: bool
    message_count: int


class UserSessionsResponse(BaseModel):
    """Response model for user's sessions list."""
    user_id: str
    sessions: List[SessionModel]
    count: int


class SessionDeleteResponse(BaseModel):
    """Response model for session deletion."""
    message: str = Field(..., description="Success message")
    session_id: str


class SessionHistoryResponse(BaseModel):
    """Response model for session history."""
    session_id: str
    messages: List[MessageModel]
    count: int
    limit: int
    offset: int


class ClearHistoryResponse(BaseModel):
    """Response model for clearing session history."""
    message: str
    session_id: str
    messages_deleted: int


# Health Check
class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    message: str
    version: str = "1.0.0"


# Error Response
class ErrorResponse(BaseModel):
    """Response model for errors."""
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# Auth Schemas
class UserSignupRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., pattern=r"^\S+@\S+\.\S+$")
    password: str = Field(..., min_length=8, max_length=64)

class UserLoginRequest(BaseModel):
    email: str = Field(...)
    password: str = Field(..., min_length=8, max_length=64)

class GoogleLoginRequest(BaseModel):
    credential: str = Field(..., description="Google JWT credential")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    name: str
    email: str

class UserProfileResponse(BaseModel):
    user_id: str
    name: str
    email: str
    profile_image: Optional[str] = None
    auth_provider: str
    created_at: datetime
    last_login: Optional[datetime] = None

