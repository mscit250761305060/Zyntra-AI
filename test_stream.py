import asyncio
from src.api.services.chat_service import chat_service
import logging

logging.basicConfig(level=logging.DEBUG)

async def main():
    try:
        async for chunk in chat_service.stream_chat("test_session_stream", "what is my name?", "test_user"):
            print(f"Chunk: {chunk}")
    except Exception as e:
        print(f"Exception: {e}")

asyncio.run(main())
