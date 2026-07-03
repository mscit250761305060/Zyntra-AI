import logging
from fastapi import HTTPException
from src.api.services.chat_service import chat_service
from src.core.config import settings

logger = logging.getLogger("zyntra.chat_controller")


class ChatController:
    """Handles the controller layer for the chatbot API."""

    async def chat(self, session_id: str, message: str, user_id: str = None) -> dict:
        """Process a chat message."""
        try:
            if not session_id:
                raise ValueError("session_id is required")
            if not message or not message.strip():
                raise ValueError("message cannot be empty")

            # Use provided user_id or default
            if not user_id:
                user_id = settings.DEFAULT_USER_ID

            response_text = await chat_service.chat(
                session_id=session_id, message=message, user_id=user_id
            )
            return {"response": response_text, "session_id": session_id, "chat_id": session_id}

        except ValueError as err:
            logger.error(f"Validation error in chat: {err}")
            raise HTTPException(status_code=400, detail=str(err))
        except Exception as e:
            logger.error(
                f"Error processing chat request for session {session_id}: {e}"
            )
            raise HTTPException(
                status_code=500, detail=f"Internal Server Error: {str(e)}"
            )

    async def get_chat_history(
        self, session_id: str, limit: int = 50, offset: int = 0
    ) -> dict:
        """Get chat history for a session."""
        try:
            if not session_id:
                raise ValueError("session_id is required")

            if limit > 1000:
                limit = 1000  # Cap limit to prevent large queries

            history = await chat_service.get_chat_history(session_id)
            return {
                "session_id": session_id,
                "chat_id": session_id,
                "messages": history,
                "count": len(history),
            }

        except ValueError as err:
            logger.error(f"Validation error in get_chat_history: {err}")
            raise HTTPException(status_code=400, detail=str(err))
        except Exception as e:
            logger.error(f"Error retrieving chat history for session {session_id}: {e}")
            raise HTTPException(
                status_code=500, detail=f"Internal Server Error: {str(e)}"
            )


chat_controller = ChatController()