"""Controller layer for session management."""
import logging
from fastapi import HTTPException
from src.api.services.session_service import session_service
from src.core.config import settings

logger = logging.getLogger("zyntra.session_controller")


class SessionController:
    """Handles HTTP requests for session management."""

    async def create_session(
        self,
        user_id: str,
        title: str = None,
        description: str = None,
        session_id: str = None,
    ) -> dict:
        """Create a new session."""
        try:
            if not user_id:
                raise ValueError("user_id is required")

            result = await session_service.create_session(
                user_id=user_id,
                title=title,
                description=description,
                session_id=session_id,
            )
            return result

        except ValueError as err:
            logger.error(f"Validation error in create_session: {err}")
            raise HTTPException(status_code=400, detail=str(err))
        except Exception as err:
            logger.error(f"Error creating session: {err}")
            raise HTTPException(
                status_code=500, detail=f"Internal Server Error: {str(err)}"
            )

    async def get_session(self, session_id: str) -> dict:
        """Retrieve session details."""
        try:
            if not session_id:
                raise ValueError("session_id is required")

            result = await session_service.get_session(session_id)
            if not result:
                raise HTTPException(status_code=404, detail="Session not found")
            return result

        except ValueError as err:
            logger.error(f"Validation error in get_session: {err}")
            raise HTTPException(status_code=400, detail=str(err))
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error retrieving session: {err}")
            raise HTTPException(
                status_code=500, detail=f"Internal Server Error: {str(err)}"
            )

    async def get_user_sessions(self, user_id: str, active_only: bool = True) -> dict:
        """Get all sessions for a user."""
        try:
            if not user_id:
                raise ValueError("user_id is required")

            sessions = await session_service.get_user_sessions(
                user_id=user_id, active_only=active_only
            )
            return {"user_id": user_id, "sessions": sessions, "count": len(sessions)}

        except ValueError as err:
            logger.error(f"Validation error in get_user_sessions: {err}")
            raise HTTPException(status_code=400, detail=str(err))
        except Exception as err:
            logger.error(f"Error retrieving user sessions: {err}")
            raise HTTPException(
                status_code=500, detail=f"Internal Server Error: {str(err)}"
            )

    async def update_session(
        self, session_id: str, title: str = None, description: str = None, is_pinned: bool = None
    ) -> dict:
        """Update session metadata."""
        try:
            if not session_id:
                raise ValueError("session_id is required")

            result = await session_service.update_session(
                session_id=session_id, title=title, description=description, is_pinned=is_pinned
            )
            if not result:
                raise HTTPException(status_code=404, detail="Session not found")
            return result

        except ValueError as err:
            logger.error(f"Validation error in update_session: {err}")
            raise HTTPException(status_code=400, detail=str(err))
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error updating session: {err}")
            raise HTTPException(
                status_code=500, detail=f"Internal Server Error: {str(err)}"
            )

    async def delete_session(self, session_id: str) -> dict:
        """Delete a session."""
        try:
            if not session_id:
                raise ValueError("session_id is required")

            success = await session_service.delete_session(session_id)
            if not success:
                raise HTTPException(status_code=404, detail="Session not found")

            return {"message": "Session deleted successfully", "session_id": session_id}

        except ValueError as err:
            logger.error(f"Validation error in delete_session: {err}")
            raise HTTPException(status_code=400, detail=str(err))
        except HTTPException:
            raise
        except Exception as err:
            logger.error(f"Error deleting session: {err}")
            raise HTTPException(
                status_code=500, detail=f"Internal Server Error: {str(err)}"
            )

    async def get_session_history(
        self, session_id: str, limit: int = 50, offset: int = 0
    ) -> dict:
        """Get conversation history for a session."""
        try:
            if not session_id:
                raise ValueError("session_id is required")

            if limit > 1000:
                limit = 1000  # Cap limit to prevent large queries

            messages = await session_service.get_session_history(
                session_id=session_id, limit=limit, offset=offset
            )
            return {
                "session_id": session_id,
                "messages": messages,
                "count": len(messages),
                "limit": limit,
                "offset": offset,
            }

        except ValueError as err:
            logger.error(f"Validation error in get_session_history: {err}")
            raise HTTPException(status_code=400, detail=str(err))
        except Exception as err:
            logger.error(f"Error retrieving session history: {err}")
            raise HTTPException(
                status_code=500, detail=f"Internal Server Error: {str(err)}"
            )

    async def clear_session_history(self, session_id: str) -> dict:
        """Clear all messages from a session."""
        try:
            if not session_id:
                raise ValueError("session_id is required")

            count = await session_service.clear_session_history(session_id)
            return {
                "message": "Session history cleared",
                "session_id": session_id,
                "messages_deleted": count,
            }

        except ValueError as err:
            logger.error(f"Validation error in clear_session_history: {err}")
            raise HTTPException(status_code=400, detail=str(err))
        except Exception as err:
            logger.error(f"Error clearing session history: {err}")
            raise HTTPException(
                status_code=500, detail=f"Internal Server Error: {str(err)}"
            )


# Global session controller instance
session_controller = SessionController()
