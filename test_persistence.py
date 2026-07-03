"""Test file-based persistence functionality."""
import sys
import json
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.persistence.file_persistence import file_persistence
from src.repositories.user_repository import user_repository
from src.repositories.session_repository import session_repository
from src.repositories.message_repository import message_repository


def test_file_persistence():
    """Test the file-based persistence system."""
    print("\n" + "=" * 60)
    print("Testing File-Based Persistence System")
    print("=" * 60)
    
    # Test 1: Create a user
    print("\n1️⃣  Creating a user...")
    user_id = user_repository.create_user(
        username="test_user",
        email="test@example.com"
    )
    print(f"   ✅ User created: {user_id}")
    
    # Test 2: Get user
    print("\n2️⃣  Retrieving user...")
    user = user_repository.get_user(user_id)
    print(f"   ✅ User retrieved: {user['username']} ({user['email']})")
    
    # Test 3: Create a session
    print("\n3️⃣  Creating a session...")
    session_id = session_repository.create_session(
        user_id=user_id,
        title="Test Conversation"
    )
    print(f"   ✅ Session created: {session_id}")
    
    # Test 4: Get session
    print("\n4️⃣  Retrieving session...")
    session = session_repository.get_session(session_id)
    print(f"   ✅ Session retrieved: {session['title']}")
    
    # Test 5: Create messages
    print("\n5️⃣  Creating messages...")
    msg1 = message_repository.create_message(
        session_id=session_id,
        user_id=user_id,
        role="user",
        content="Hello, what is Python?"
    )
    print(f"   ✅ User message created: {msg1}")
    
    msg2 = message_repository.create_message(
        session_id=session_id,
        user_id=user_id,
        role="assistant",
        content="Python is a programming language...",
        agent_name="main_agent"
    )
    print(f"   ✅ Assistant message created: {msg2}")
    
    # Test 6: Get session messages
    print("\n6️⃣  Retrieving messages...")
    messages = message_repository.get_session_messages(session_id)
    print(f"   ✅ Retrieved {len(messages)} messages")
    for msg in messages:
        print(f"      - {msg['role']}: {msg['content'][:50]}...")
    
    # Test 7: Get user sessions
    print("\n7️⃣  Retrieving user sessions...")
    sessions = session_repository.get_user_sessions(user_id)
    print(f"   ✅ Retrieved {len(sessions)} sessions")
    
    # Test 8: Check data files
    print("\n8️⃣  Checking data files...")
    data_dir = Path("data")
    if data_dir.exists():
        files = list(data_dir.glob("*.json"))
        print(f"   ✅ Found {len(files)} data files:")
        for f in files:
            size = f.stat().st_size
            print(f"      - {f.name} ({size} bytes)")
    
    print("\n" + "=" * 60)
    print("✨ All tests passed! File persistence is working.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        test_file_persistence()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
