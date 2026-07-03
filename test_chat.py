import asyncio
from src.api.services.chat_service import chat_service
import logging

logging.basicConfig(level=logging.DEBUG)

async def main():
    try:
        res = await chat_service._generate_response("what is my name?", "test_session", "test_user")
        print(f"Response: {res}")
    except Exception as e:
        print(f"Exception: {e}")

asyncio.run(main())
