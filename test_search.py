import asyncio
import json
import logging
logging.basicConfig(level=logging.DEBUG)

from src.agents.runner.main_runner import main_runner
from google.genai import types

async def main():
    new_msg = types.Content(role='user', parts=[types.Part.from_text(text='what is today news of AI?')])
    async for e in main_runner.run_async(user_id='test', session_id='test1', new_message=new_msg):
        if hasattr(e, 'content') and e.content:
            print('CONT:', e.content.parts[0].text if e.content.parts else '')
        else:
            print('EVENT:', e)

asyncio.run(main())
