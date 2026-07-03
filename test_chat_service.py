"""Test if the chat service can handle messages."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.api.services.chat_service import chat_service
from src.repositories.session_repository import session_repository


async def test_chat():
    """Test sending a message to the chat service."""
    print("\n" + "=" * 60)
    print("Testing Chat Service")
    print("=" * 60)

    try:
        # Create a test user and session
        print("\n1️⃣  Creating test session...")
        user_id = "test_user_123"
        session_id = "test_session_123"
        
        session_repository.create_session(
            user_id=user_id,
            session_id=session_id,
            title="Test Chat Session"
        )
        print(f"   ✅ Session created: {session_id}")

        # Test sending a message
        print("\n2️⃣  Sending test message to agent...")
        test_message = "Hello! What is Python?"
        
        response = await chat_service.chat(
            session_id=session_id,
            message=test_message,
            user_id=user_id
        )
        
        print(f"   ✅ Message sent successfully")
        print(f"\n📝 Your message: {test_message}")
        print(f"\n🤖 Agent response:\n   {response}")

        # Test another message
        print("\n3️⃣  Sending second message...")
        test_message2 = "Can you help me?"
        
        response2 = await chat_service.chat(
            session_id=session_id,
            message=test_message2,
            user_id=user_id
        )
        
        print(f"   ✅ Message sent successfully")
        print(f"\n📝 Your message: {test_message2}")
        print(f"\n🤖 Agent response:\n   {response2}")

        # Check message history
        print("\n4️⃣  Checking message history...")
        history = await chat_service.get_chat_history(session_id)
        print(f"   ✅ Retrieved {len(history)} messages:")
        for i, msg in enumerate(history, 1):
            role = "You" if msg["role"] == "user" else "Agent"
            content = msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
            print(f"      {i}. {role}: {content}")

        print("\n" + "=" * 60)
        print("✨ Chat Service Test Passed!")
        print("=" * 60 + "\n")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_chat())
    sys.exit(0 if result else 1)
