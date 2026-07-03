import logging
import os
from uuid import uuid4
from src.repositories.message_repository import message_repository
from src.repositories.session_repository import session_repository
from src.core.config import settings

logger = logging.getLogger("zyntra.chat_service")


class ChatService:
    """
    Handles chat processing with:
    - Message persistence to file storage
    - Conversation context management
    - Google AI integration (with fallback)
    """

    async def chat(
        self, session_id: str, message: str, user_id: str = "default_user"
    ) -> str:
        """
        Process a chat message:
        1. Ensure session exists
        2. Persist user message
        3. Generate response (from AI or fallback)
        4. Persist agent response
        5. Return response text
        """
        try:
            # Ensure session exists
            if not session_repository.session_exists(session_id):
                session_repository.create_session(user_id=user_id, session_id=session_id)

            # Persist user message to file storage
            user_message_id = message_repository.create_message(
                session_id=session_id,
                user_id=user_id,
                role="user",
                content=message,
            )
            logger.info(f"User message persisted: {user_message_id}")

            # Generate response
            response_text = await self._generate_response(message, session_id, user_id, exclude_message_id=user_message_id)

            # Persist agent response
            agent_response_id = message_repository.create_message(
                session_id=session_id,
                user_id=user_id,
                role="assistant",
                content=response_text,
                agent_name="main_agent",
            )
            logger.info(f"Agent response persisted: {agent_response_id}")

            # Auto-title if this is the first message
            import asyncio
            asyncio.create_task(self._auto_title(session_id, message))

            return response_text

        except Exception as e:
            logger.error(f"Error in chat service for session '{session_id}': {e}")
            raise
    async def stream_chat(
        self, session_id: str, message: str, user_id: str = "default_user"
    ):
        """
        Process a chat message and yield Server-Sent Events (SSE) for streaming.
        """
        try:
            import json
            # Ensure session exists
            if not session_repository.session_exists(session_id):
                session_repository.create_session(user_id=user_id, session_id=session_id)

            # Persist user message
            user_message_id = message_repository.create_message(
                session_id=session_id,
                user_id=user_id,
                role="user",
                content=message,
            )
            logger.info(f"User message persisted: {user_message_id}")

            await self._preload_adk_session(session_id, user_id, exclude_message_id=user_message_id)

            from src.agents.runner.main_runner import main_runner
            from google.genai import types

            new_message = types.Content(role='user', parts=[types.Part.from_text(text=message)])
            from src.agents.sessions.session_manager import session_manager
            adk_session = await session_manager.get_session(session_id, app_name="main_orchestrator", user_id=user_id)
            if adk_session:
                logger.info(f"EVENTS SENT TO MODEL: {adk_session.events}")
                
            response_text = ""
            async for event in main_runner.run_async(user_id=user_id, session_id=session_id, new_message=new_message):
                if hasattr(event, "content") and event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            chunk = part.text
                            response_text += chunk
                            yield f"data: {json.dumps({'chunk': chunk})}\n\n"

            if not response_text:
                logger.warning(f"Empty response from ADK runner for session {session_id}")
                fallback = self._get_fallback_response(message)
                response_text = fallback
                yield f"data: {json.dumps({'chunk': fallback})}\n\n"

            # Persist agent response
            agent_response_id = message_repository.create_message(
                session_id=session_id,
                user_id=user_id,
                role="assistant",
                content=response_text,
                agent_name="main_agent",
            )
            logger.info(f"Agent response persisted: {agent_response_id}")
            
            import asyncio
            asyncio.create_task(self._auto_title(session_id, message))
            
            from src.services.rag_service import rag_service
            citations = rag_service.last_search_results.pop(user_id, None)
            if citations:
                yield f"data: {json.dumps({'type': 'citations', 'data': citations})}\n\n"
            
            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            import json
            logger.error(f"Error in stream_chat for session '{session_id}': {e}")
            fallback = self._get_fallback_response(message)
            yield f"data: {json.dumps({'chunk': fallback, 'error': str(e)})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"

    async def voice_chat(
        self, session_id: str, user_id: str, audio_bytes: bytes, mime_type: str = "audio/webm"
    ) -> str:
        """
        Process a voice chat message using Google ADK main_runner.
        """
        try:
            # Ensure session exists
            if not session_repository.session_exists(session_id):
                session_repository.create_session(user_id=user_id, session_id=session_id)

            await self._preload_adk_session(session_id, user_id)

            from src.agents.runner.main_runner import main_runner
            from google.genai import types

            new_message = types.Content(role='user', parts=[types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)])
            
            response_text = ""
            async for event in main_runner.run_async(user_id=user_id, session_id=session_id, new_message=new_message):
                if hasattr(event, "content") and event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            response_text += part.text

            if not response_text:
                logger.warning(f"Empty response from ADK runner for session {session_id}")
                return "I'm sorry, I couldn't process your audio."

            # Persist user message (Audio indicator)
            message_repository.create_message(
                session_id=session_id,
                user_id=user_id,
                role="user",
                content="🎙️ [Audio Message]",
            )

            # Persist agent response
            message_repository.create_message(
                session_id=session_id,
                user_id=user_id,
                role="assistant",
                content=response_text,
                agent_name="main_agent",
            )
            
            return response_text

        except Exception as e:
            logger.error(f"Error in voice_chat for session '{session_id}': {e}")
            return f"Sorry, there was an error processing your audio: {str(e)}"

    async def _generate_response(
        self, message: str, session_id: str, user_id: str, exclude_message_id: str = None
    ) -> str:
        """
        Generate a response using Google ADK main_runner or fallback.
        """
        try:
            await self._preload_adk_session(session_id, user_id, exclude_message_id=exclude_message_id)
            from src.agents.runner.main_runner import main_runner
            from google.genai import types

            new_message = types.Content(role='user', parts=[types.Part.from_text(text=message)])
            
            response_text = ""
            async for event in main_runner.run_async(user_id=user_id, session_id=session_id, new_message=new_message):
                if hasattr(event, "content") and event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            response_text += part.text

            if not response_text:
                logger.warning(f"Empty response from ADK runner for session {session_id}")
                return self._get_fallback_response(message)

            logger.info(f"Response generated from ADK runner for session {session_id}")
            return response_text

        except Exception as e:
            logger.error(f"Error generating response from ADK runner: {e}")
            return self._get_fallback_response(message)

    def _get_fallback_response(self, message: str) -> str:
        """
        Provide a fallback response when AI is not available.
        """
        return f"I received your message: \"{message}\". I'm currently using a fallback response system because the AI is unavailable. Please check your GEMINI_API_KEY and API quota."

    async def _auto_title(self, session_id: str, first_message: str):
        """Automatically generate and set a title for a new session based on the first message."""
        try:
            session = session_repository.get_session(session_id)
            if not session or (session.get("title") and not session.get("title").startswith("Session ") and session.get("title") != "New sequence"):
                return
                
            # Double check message count is small (e.g., 2 for 1 user and 1 assistant message)
            count = message_repository.get_session_message_count(session_id)
            if count > 2:
                return
                
            # Use the first chat message as the title
            new_title = first_message.strip()
            if len(new_title) > 30:
                new_title = new_title[:27] + "..."
                
            session_repository.update_session(session_id=session_id, title=new_title)
            logger.info(f"Auto-generated title for session {session_id}: {new_title}")
        except Exception as e:
            logger.error(f"Error auto-titling session {session_id}: {e}")

    async def get_chat_history(self, session_id: str) -> list:
        """Retrieve full conversation history for a session."""
        try:
            history = message_repository.get_session_messages(session_id, limit=1000)
            logger.info(f"Retrieved {len(history)} messages for session {session_id}")
            return history
        except Exception as e:
            logger.error(f"Error retrieving chat history for session '{session_id}': {e}")
            raise

    async def _preload_adk_session(self, session_id: str, user_id: str, exclude_message_id: str = None):
        """Preload database messages into ADK in-memory session to maintain context."""
        try:
            from src.agents.sessions.session_manager import session_manager
            from google.adk.events.event import Event
            from google.genai import types
            import uuid

            adk_session = await session_manager.get_session(session_id, app_name="main_orchestrator", user_id=user_id)
            if not adk_session:
                adk_session = await session_manager.memory_session.create(session_id, app_name="main_orchestrator", user_id=user_id)
            
            # ADK returns a copy of the session. To modify memory for the runner, we must access the storage session
            storage_session = session_manager.session_service.sessions.get("main_orchestrator", {}).get(user_id, {}).get(session_id)
            if not storage_session:
                return

            if not storage_session.events:
                # Retrieve all messages for the current session
                db_messages = message_repository.get_session_messages(session_id, limit=1000)
                
                # If this is a new session with no history, load the last 10 messages from the user's previous sessions
                if not db_messages:
                    db_messages = message_repository.get_user_messages(user_id, limit=10)
                    # get_user_messages returns sorted by descending (newest first). We need to reverse them for chronological order.
                    db_messages = list(reversed(db_messages))
                    logger.info(f"Loaded {len(db_messages)} cross-session messages for user {user_id}")
                else:
                    db_messages = db_messages[-10:]
                
                # Ensure the first message is from a 'user' to comply with Gemini API strict alternating rules
                while db_messages and db_messages[0].get("role") != "user":
                    db_messages.pop(0)

                for msg in db_messages:
                    if exclude_message_id and msg.get("message_id") == exclude_message_id:
                        continue
                    if msg.get("content") == "🎙️ [Audio Message]":
                        continue
                    
                    if msg["role"] == "assistant":
                        author = "chatbot"
                        role = "model"
                    else:
                        author = "user"
                        role = "user"
                        
                    event = Event(
                        author=author,
                        content=types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]),
                        id=msg.get("message_id", str(uuid.uuid4()))
                    )
                    storage_session.events.append(event)
                logger.info(f"Preloaded {len(storage_session.events)} events into ADK session {session_id}")
            
            # Enforce memory limit: keep only the last 10 messages in memory for EVERY query
            if len(storage_session.events) > 10:
                storage_session.events = storage_session.events[-10:]
                
            # Ensure the first message is from a 'user' to comply with Gemini API strict alternating rules
            while storage_session.events and getattr(storage_session.events[0].content, 'role', '') != 'user':
                storage_session.events.pop(0)
                
            logger.info(f"Trimmed ADK session {session_id} to {len(storage_session.events)} events")
                
        except Exception as e:
            logger.warning(f"Failed to preload ADK session context for {session_id}: {e}")

chat_service = ChatService()