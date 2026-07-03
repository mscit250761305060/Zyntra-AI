import asyncio
import sys
import os
sys.path.append('d:/chatbot/code')
from src.core.config import settings
from src.agents.runner.main_runner import main_runner
from google.genai import types

async def run():
    try:
        new_message = types.Content(role='user', parts=[types.Part.from_text(text='What is capital of india?')])
        response_text = ''
        async for event in main_runner.run_async(user_id='test', session_id='test', new_message=new_message):
            if hasattr(event, 'content') and event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text: 
                        response_text += part.text
        print('RESPONSE:', response_text)
    except Exception as e:
        print('ERROR:', repr(e))

if __name__ == '__main__':
    asyncio.run(run())
