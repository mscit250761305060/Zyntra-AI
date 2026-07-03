import logging
from fastapi import APIRouter, HTTPException, Depends
from src.api.middleware.auth_middleware import get_current_user
from src.api.controllers.session_controller import session_controller
from src.models.schemas import (
    SessionCreateRequest,
    SessionUpdateRequest,
    SessionCreateResponse,
    SessionDetailsResponse,
    UserSessionsResponse,
    SessionDeleteResponse,
    SessionHistoryResponse,
    ClearHistoryResponse,
)

logger = logging.getLogger("zyntra.session_routes")

router = APIRouter(prefix="/api/v1/sessions", tags=["Sessions"])


@router.post("/create", response_model=SessionCreateResponse)
async def create_session(request: SessionCreateRequest, current_user: dict = Depends(get_current_user)):
    """
    Create a new chat session.
    
    - **user_id**: Required user identifier (will be overridden by auth)
    - **title**: Optional session title
    - **description**: Optional session description
    - **session_id**: Optional custom session ID
    """
    request.user_id = current_user["user_id"]
    
    result = await session_controller.create_session(
        user_id=request.user_id,
        title=request.title,
        description=request.description,
        session_id=request.session_id,
    )
    return result


@router.get("/search")
async def search_sessions(q: str, current_user: dict = Depends(get_current_user)):
    """Search sessions by message content."""
    from src.repositories.message_repository import message_repository
    session_ids = message_repository.search_messages(current_user["user_id"], q)
    return {"session_ids": session_ids}


@router.get("/{session_id}", response_model=SessionDetailsResponse)
async def get_session(session_id: str, current_user: dict = Depends(get_current_user)):
    """
    Retrieve details for a specific session.
    
    - **session_id**: The session identifier
    """
    result = await session_controller.get_session(session_id)
    if result.get("user_id") != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to access this session")
    return result


@router.get("/me", response_model=UserSessionsResponse)
async def get_my_sessions(active_only: bool = True, current_user: dict = Depends(get_current_user)):
    """
    Get all sessions for the currently authenticated user.
    
    - **active_only**: Filter to active sessions only (default: true)
    """
    result = await session_controller.get_user_sessions(
        user_id=current_user["user_id"], active_only=active_only
    )
    return result

@router.get("/user/{user_id}", response_model=UserSessionsResponse)
async def get_user_sessions(user_id: str, active_only: bool = True, current_user: dict = Depends(get_current_user)):
    """
    Get all sessions for a specific user.
    
    - **user_id**: The user identifier
    - **active_only**: Filter to active sessions only (default: true)
    """
    if user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to access these sessions")
        
    result = await session_controller.get_user_sessions(
        user_id=user_id, active_only=active_only
    )
    return result


@router.put("/{session_id}", response_model=SessionDetailsResponse)
async def update_session(session_id: str, request: SessionUpdateRequest, current_user: dict = Depends(get_current_user)):
    """
    Update session metadata.
    
    - **session_id**: The session identifier
    - **title**: New session title
    - **description**: New session description
    """
    session = await session_controller.get_session(session_id)
    if session.get("user_id") != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this session")
        
    result = await session_controller.update_session(
        session_id=session_id, title=request.title, description=request.description, is_pinned=request.is_pinned
    )
    return result


@router.delete("/{session_id}", response_model=SessionDeleteResponse)
async def delete_session(session_id: str, current_user: dict = Depends(get_current_user)):
    """
    Delete a session and all related data.
    
    - **session_id**: The session identifier
    """
    session = await session_controller.get_session(session_id)
    if session.get("user_id") != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this session")
        
    result = await session_controller.delete_session(session_id)
    return result


@router.get("/{session_id}/history", response_model=SessionHistoryResponse)
async def get_session_history(
    session_id: str, limit: int = 50, offset: int = 0, current_user: dict = Depends(get_current_user)
):
    """
    Retrieve conversation history for a session.
    
    - **session_id**: The session identifier
    - **limit**: Maximum number of messages (default: 50, max: 1000)
    - **offset**: Pagination offset (default: 0)
    """
    session = await session_controller.get_session(session_id)
    if session.get("user_id") != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to access this session history")
        
    result = await session_controller.get_session_history(
        session_id=session_id, limit=limit, offset=offset
    )
    return result


@router.delete("/{session_id}/history", response_model=ClearHistoryResponse)
async def clear_session_history(session_id: str, current_user: dict = Depends(get_current_user)):
    """
    Clear all messages from a session (keeps the session).
    
    - **session_id**: The session identifier
    """
    session = await session_controller.get_session(session_id)
    if session.get("user_id") != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to clear this session history")
        
    result = await session_controller.clear_session_history(session_id)
    return result
