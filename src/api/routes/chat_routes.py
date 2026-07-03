import logging
from fastapi import APIRouter, HTTPException, Depends, Form, File, UploadFile
from src.services.rag_service import rag_service
from src.api.middleware.auth_middleware import get_current_user
from src.api.controllers.chat_controller import chat_controller
from src.models.schemas import (
    ChatRequest,
    ChatResponse,
    ChatHistoryResponse,
    MessageModel,
    ChatListResponse,
    ChatHistoryItemResponse,
)

logger = logging.getLogger("zyntra.chat_routes")

router = APIRouter(prefix="/api/v1", tags=["Chat"])


from typing import List

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    # Accept JSON body or multipart form data
    # JSON parameters (for existing clients)
    request: ChatRequest = None,
    # Multipart form parameters (for new attachment flow)
    session_id: str = Form(None),
    message: str = Form(None),
    files: List[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user)
) -> ChatResponse:
    """Handle chat messages with optional document attachment.

    Supports both the original JSON payload and multipart/form-data where a file can be uploaded together with the message.
    """
    # Determine user_id from auth
    user_id = current_user.get("user_id")

    # Determine actual session id – prefer explicit JSON field, then form field, then generate new
    actual_session_id = None
    if request:
        # Existing JSON request path
        request.user_id = user_id
        actual_session_id = request.chat_id or request.session_id
        msg_text = request.message
    else:
        # Multipart path
        actual_session_id = session_id
        msg_text = message

    if not actual_session_id:
        import uuid
        actual_session_id = str(uuid.uuid4())

    # If files are attached, process them via RAGService before proceeding with chat
    if files is not None:
        import os, tempfile, shutil
        for file in files:
            if not file.filename:
                continue
            # Save temporary file
            suffix = os.path.splitext(file.filename)[1]
            temp_dir = tempfile.mkdtemp()
            temp_path = os.path.join(temp_dir, f"{user_id}_{file.filename}")
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            # Process document (extract, embed)
            rag_service.process_document(user_id, temp_path, file.filename)
            # Cleanup temp file and directory
            try:
                os.remove(temp_path)
                shutil.rmtree(temp_dir)
            except Exception:
                pass

    # Call chat controller with the message (or empty string if none)
    result = await chat_controller.chat(
        session_id=actual_session_id,
        message=msg_text or "",
        user_id=user_id,
    )
    return result


from fastapi.responses import StreamingResponse

@router.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    """
    Stream a message response using Server-Sent Events (SSE).
    """
    # Force user isolation
    request.user_id = current_user["user_id"]
    
    # Import the service directly if not part of controller
    from src.api.services.chat_service import chat_service
    
    import uuid
    actual_session_id = request.chat_id or request.session_id or str(uuid.uuid4())
    
    return StreamingResponse(
        chat_service.stream_chat(
            session_id=actual_session_id,
            message=request.message,
            user_id=request.user_id,
        ),
        media_type="text/event-stream"
    )

from fastapi import UploadFile, File, Form
from fastapi.responses import FileResponse
import os
import uuid

@router.post("/chat/voice")
async def chat_voice_endpoint(
    audio: UploadFile = File(...),
    session_id: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Process voice input and return voice output.
    """
    from src.api.services.chat_service import chat_service
    from src.services.voice_service import voice_service, AUDIO_DIR
    
    audio_bytes = await audio.read()
    user_id = current_user["user_id"]
    
    # 1. Process with ADK Main Runner
    response_text = await chat_service.voice_chat(
        session_id=session_id,
        user_id=user_id,
        audio_bytes=audio_bytes,
        mime_type=audio.content_type or "audio/webm"
    )
    
    # 2. Synthesize to Speech
    output_filename = f"response_{uuid.uuid4()}.mp3"
    output_path = os.path.join(AUDIO_DIR, output_filename)
    
    success = await voice_service.synthesize(response_text, output_path)
    if success and os.path.exists(output_path):
        return FileResponse(output_path, media_type="audio/mpeg")
    else:
        raise HTTPException(status_code=500, detail="Failed to synthesize audio")


from pydantic import BaseModel

class TTSRequest(BaseModel):
    text: str

@router.post("/chat/tts")
async def chat_tts_endpoint(
    request: TTSRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Convert arbitrary text to speech and return the MP3 file.
    """
    from src.services.voice_service import voice_service, AUDIO_DIR
    
    output_filename = f"tts_{uuid.uuid4()}.mp3"
    output_path = os.path.join(AUDIO_DIR, output_filename)
    
    success = await voice_service.synthesize(request.text, output_path)
    if success and os.path.exists(output_path):
        return FileResponse(output_path, media_type="audio/mpeg")
    else:
        raise HTTPException(status_code=500, detail="Failed to synthesize audio")

@router.get("/chat/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(session_id: str, limit: int = 50, offset: int = 0, current_user: dict = Depends(get_current_user)):
    """
    Retrieve the complete chat history for a session.
    
    - **session_id**: The session identifier
    - **limit**: Maximum number of messages to retrieve (default: 50, max: 1000)
    - **offset**: Pagination offset (default: 0)
    """
    # Note: controller will use current_user to verify session ownership in a complete system, 
    # but at least this endpoint is now authenticated.
    result = await chat_controller.get_chat_history(
        session_id=session_id, limit=limit, offset=offset
    )
    return result

@router.get("/chat/history", response_model=ChatListResponse)
async def get_all_chat_history(current_user: dict = Depends(get_current_user)):
    """
    Retrieve all chat sessions for the logged-in user (ChatGPT-style).
    Ordered by the most recently updated.
    """
    from src.api.controllers.session_controller import session_controller
    from src.repositories.message_repository import message_repository
    
    user_id = current_user["user_id"]
    result = await session_controller.get_user_sessions(user_id=user_id, active_only=True)
    sessions = result.get("sessions", [])
    
    chats = []
    for s in sessions:
        chat_id = s["session_id"]
        # Fetch last message
        messages = message_repository.get_session_messages(chat_id, limit=1)
        last_message = messages[-1]["content"] if messages else None
        
        chats.append(ChatHistoryItemResponse(
            chat_id=chat_id,
            title=s.get("title") or "New Chat",
            last_message=last_message,
            created_at=s["created_at"],
            updated_at=s["updated_at"]
        ))
    
    # Sort by updated_at descending
    chats.sort(key=lambda x: x.updated_at, reverse=True)
    
    return ChatListResponse(chats=chats)

@router.delete("/chat/history/{chat_id}")
async def delete_chat_history(chat_id: str, current_user: dict = Depends(get_current_user)):
    """
    Delete a chat and all associated messages (ChatGPT-style).
    """
    from src.api.controllers.session_controller import session_controller
    # Verify ownership
    session = await session_controller.get_session(chat_id)
    if session.get("user_id") != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this chat")
        
    await session_controller.delete_session(chat_id)
    return {"message": "Chat deleted successfully", "chat_id": chat_id}