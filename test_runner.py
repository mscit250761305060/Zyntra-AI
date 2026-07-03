import asyncio
import os
import sys

# Setup paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.agents.runner.main_runner import main_runner
from google.genai import types

async def test():
    user_id = "test_user"
    session_id = "test_session_123"
    
    new_message = types.Content(role='user', parts=[types.Part.from_text(text="What is AI?")])
    
    response_text = ""
    print("Running runner...")
    async for event in main_runner.run_async(user_id=user_id, session_id=session_id, new_message=new_message):
        print("Got event:", event.__class__.__name__)
        if hasattr(event, "content") and event.content:
            print("Content:", event.content)
            if event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text
        if hasattr(event, "error_message") and event.error_message:
            print("Error message:", event.error_message)

    print("Final response:", response_text)

asyncio.run(test())
