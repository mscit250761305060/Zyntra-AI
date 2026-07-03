import asyncio
from fastapi.testclient import TestClient
from main import app
from src.persistence.file_persistence import file_persistence

client = TestClient(app)

def test_auth_flow():
    print("Testing auth flow...")
    
    # Clean up dummy user if exists
    email = "testauth@example.com"
    password = "password123"
    
    # 1. Signup
    print("1. Signup")
    res = client.post("/api/v1/auth/signup", json={"name": "Test User", "email": email, "password": password})
    assert res.status_code in (200, 400), f"Signup failed: {res.text}"
        
    # 2. Login
    print("2. Login")
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, f"Login failed: {res.text}"
        
    tokens = res.json()
    access_token = tokens["access_token"]
    
    # 3. Get Me
    print("3. Get Me")
    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 200, f"Me failed: {res.text}"
        
    print("Auth flow successful!")

if __name__ == "__main__":
    test_auth_flow()
