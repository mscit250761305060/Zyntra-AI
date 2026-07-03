import asyncio
import httpx

async def run():
    async with httpx.AsyncClient() as client:
        response = await client.post('http://localhost:8000/api/v1/chat', json={
            'session_id': 'session123',
            'message': 'What is capital of india?'
        })
        print(response.json())

if __name__ == '__main__':
    asyncio.run(run())
