# API Testing Guide - cURL Examples

Complete cURL examples for testing all API endpoints. Copy and paste directly into PowerShell or Command Prompt.

## Prerequisites

```bash
# Start the server first
python main.py

# In another terminal, ensure you're in the project directory
cd d:\chatbot\code
```

## 1. Health & Info Endpoints

### Health Check
```bash
curl -X GET http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "message": "Zyntra AI is running",
  "version": "1.0.0"
}
```

### Application Info
```bash
curl -X GET http://localhost:8000/api/v1/info
```

### Root Endpoint
```bash
curl -X GET http://localhost:8000/
```

## 2. Session Management Endpoints

### Create a Session

```bash
curl -X POST http://localhost:8000/api/v1/sessions/create ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\":\"user-123\",\"title\":\"My Chat Session\",\"description\":\"Test session\"}"
```

**Response:**
```json
{
  "session_id": "abc-123-xyz",
  "user_id": "user-123",
  "title": "My Chat Session",
  "description": "Test session",
  "created_at": "2026-06-23T10:00:00",
  "is_active": true
}
```

**Save session_id for next requests:**
```powershell
# PowerShell - save for later use
$session_id = "abc-123-xyz"
```

### Get Session Details

```bash
curl -X GET http://localhost:8000/api/v1/sessions/abc-123-xyz
```

**Response:**
```json
{
  "session_id": "abc-123-xyz",
  "user_id": "user-123",
  "title": "My Chat Session",
  "description": "Test session",
  "app_name": "chatbot",
  "created_at": "2026-06-23T10:00:00",
  "updated_at": "2026-06-23T10:00:00",
  "last_accessed_at": "2026-06-23T10:00:00",
  "is_active": true,
  "message_count": 0
}
```

### Get All Sessions for a User

```bash
curl -X GET http://localhost:8000/api/v1/sessions/user/user-123
```

**Response:**
```json
{
  "user_id": "user-123",
  "sessions": [
    {
      "session_id": "abc-123-xyz",
      "title": "My Chat Session",
      "message_count": 0,
      ...
    }
  ],
  "count": 1
}
```

### Update Session

```bash
curl -X PUT http://localhost:8000/api/v1/sessions/abc-123-xyz ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"Updated Title\",\"description\":\"Updated description\"}"
```

### Get Session History

```bash
curl -X GET "http://localhost:8000/api/v1/sessions/abc-123-xyz/history?limit=50&offset=0"
```

### Clear Session History

```bash
curl -X DELETE http://localhost:8000/api/v1/sessions/abc-123-xyz/history
```

**Response:**
```json
{
  "message": "Session history cleared",
  "session_id": "abc-123-xyz",
  "messages_deleted": 5
}
```

### Delete Session

```bash
curl -X DELETE http://localhost:8000/api/v1/sessions/abc-123-xyz
```

**Response:**
```json
{
  "message": "Session deleted successfully",
  "session_id": "abc-123-xyz"
}
```

## 3. Chat Endpoints

### Send a Message

```bash
curl -X POST http://localhost:8000/api/v1/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"session_id\":\"abc-123-xyz\",\"message\":\"How do I write a Python function?\",\"user_id\":\"user-123\"}"
```

**Response:**
```json
{
  "response": "To write a Python function, you can use the def keyword...",
  "session_id": "abc-123-xyz"
}
```

### Get Chat History

```bash
curl -X GET "http://localhost:8000/api/v1/chat/history/abc-123-xyz?limit=50&offset=0"
```

**Response:**
```json
{
  "session_id": "abc-123-xyz",
  "messages": [
    {
      "id": 1,
      "message_id": "msg-123",
      "session_id": "abc-123-xyz",
      "user_id": "user-123",
      "role": "user",
      "content": "How do I write a Python function?",
      "agent_name": null,
      "message_type": "text",
      "created_at": "2026-06-23T10:00:00"
    },
    {
      "id": 2,
      "message_id": "msg-124",
      "session_id": "abc-123-xyz",
      "user_id": "user-123",
      "role": "chatbot",
      "content": "To write a Python function...",
      "agent_name": "chatbot",
      "message_type": "text",
      "created_at": "2026-06-23T10:01:00"
    }
  ],
  "count": 2
}
```

## Complete Workflow Example

Test the entire system with this complete workflow:

```bash
# 1. Create a session
$response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/sessions/create" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"user_id":"test-user","title":"Test Session"}'

$session = $response.Content | ConvertFrom-Json
$session_id = $session.session_id
Write-Host "Created session: $session_id"

# 2. Send first message
$response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/chat" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body "{`"session_id`":`"$session_id`",`"message`":`"What is Python?`"}"

$chat1 = $response.Content | ConvertFrom-Json
Write-Host "Agent response: $($chat1.response)"

# 3. Send second message (context maintained)
$response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/chat" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body "{`"session_id`":`"$session_id`",`"message`":`"Write a function to calculate factorial`"}"

$chat2 = $response.Content | ConvertFrom-Json
Write-Host "Agent response: $($chat2.response)"

# 4. Get history
$response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/chat/history/$session_id"
$history = $response.Content | ConvertFrom-Json
Write-Host "Total messages: $($history.count)"
$history.messages | ForEach-Object { Write-Host "- $($_.role): $($_.content.Substring(0, 50))..." }

# 5. Get session info
$response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/sessions/$session_id"
$session_info = $response.Content | ConvertFrom-Json
Write-Host "Session has $($session_info.message_count) messages"
```

## Advanced Query Examples

### Pagination Through History

```bash
# Get first 10 messages
curl -X GET "http://localhost:8000/api/v1/chat/history/abc-123-xyz?limit=10&offset=0"

# Get next 10 messages
curl -X GET "http://localhost:8000/api/v1/chat/history/abc-123-xyz?limit=10&offset=10"

# Get last 5 messages
curl -X GET "http://localhost:8000/api/v1/chat/history/abc-123-xyz?limit=5&offset=0"
```

### Filter Sessions by Status

```bash
# Get only active sessions
curl -X GET "http://localhost:8000/api/v1/sessions/user/user-123?active_only=true"

# Get all sessions (including inactive)
curl -X GET "http://localhost:8000/api/v1/sessions/user/user-123?active_only=false"
```

## Error Response Examples

### 400 - Bad Request

```bash
# Missing required field
curl -X POST http://localhost:8000/api/v1/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"session_id\":\"\"}"
```

**Response:**
```json
{
  "detail": "session_id is required"
}
```

### 404 - Not Found

```bash
curl -X GET http://localhost:8000/api/v1/sessions/invalid-session
```

**Response:**
```json
{
  "detail": "Session not found"
}
```

### 500 - Server Error

**Response:**
```json
{
  "detail": "Internal Server Error: <error message>"
}
```

## Testing with Swagger UI

Instead of cURL, you can test directly in the browser:

1. Open: http://localhost:8000/api/docs
2. Click on any endpoint
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"
6. View response

## PowerShell Script for Testing

Save as `test_api.ps1`:

```powershell
# API base URL
$baseUrl = "http://localhost:8000"
$user_id = "test-user-$(Get-Random)"

Write-Host "🧪 Testing ADK Chatbot API..."
Write-Host ""

# 1. Health Check
Write-Host "1. Health Check..."
$health = Invoke-WebRequest -Uri "$baseUrl/health" | ConvertFrom-Json
Write-Host "✓ Status: $($health.status)"
Write-Host ""

# 2. Create Session
Write-Host "2. Creating Session..."
$sessionResp = Invoke-WebRequest -Uri "$baseUrl/api/v1/sessions/create" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body @"
{"user_id":"$user_id","title":"Test Session"}
"@
$session = $sessionResp.Content | ConvertFrom-Json
$session_id = $session.session_id
Write-Host "✓ Session created: $session_id"
Write-Host ""

# 3. Send Messages
Write-Host "3. Sending Messages..."
$messages = @(
    "What is machine learning?",
    "Can you give me an example?",
    "How would I implement this in Python?"
)

foreach ($msg in $messages) {
    Write-Host "  Sending: $msg"
    $chatResp = Invoke-WebRequest -Uri "$baseUrl/api/v1/chat" `
      -Method POST `
      -Headers @{"Content-Type"="application/json"} `
      -Body @"
{"session_id":"$session_id","message":"$msg","user_id":"$user_id"}
"@
    $chat = $chatResp.Content | ConvertFrom-Json
    Write-Host "  Response: $($chat.response.Substring(0, 100))..."
    Write-Host ""
}

# 4. Get History
Write-Host "4. Getting Chat History..."
$historyResp = Invoke-WebRequest -Uri "$baseUrl/api/v1/chat/history/$session_id"
$history = $historyResp.Content | ConvertFrom-Json
Write-Host "✓ Total messages: $($history.count)"
$history.messages | ForEach-Object {
    Write-Host "  - $($_.role): $($_.content.Substring(0, 50))..."
}
Write-Host ""

# 5. Get All Sessions
Write-Host "5. Getting All Sessions..."
$sessionsResp = Invoke-WebRequest -Uri "$baseUrl/api/v1/sessions/user/$user_id"
$sessions = $sessionsResp.Content | ConvertFrom-Json
Write-Host "✓ Total sessions: $($sessions.count)"
Write-Host ""

Write-Host "✅ All tests passed!"
```

Run with:
```bash
powershell -ExecutionPolicy Bypass -File test_api.ps1
```

## Performance Testing

```bash
# Send 10 messages in sequence
for /L %i in (1,1,10) do (
    curl -X POST http://localhost:8000/api/v1/chat ^
      -H "Content-Type: application/json" ^
      -d "{\"session_id\":\"abc-123-xyz\",\"message\":\"Test message %i\"}"
)
```

## Batch API Testing

```bash
# Using jq for JSON processing (requires jq installation)
curl -s http://localhost:8000/api/v1/sessions/user/user-123 | jq '.sessions | length'

# Using PowerShell
$sessions = (Invoke-WebRequest -Uri "http://localhost:8000/api/v1/sessions/user/user-123" | ConvertFrom-Json)
Write-Host "Sessions: $($sessions.count)"
```

---

## Common Patterns

### Pattern 1: Create Session and Send Message

```bash
# Variables
set user_id=user-123

# Create session
curl -X POST http://localhost:8000/api/v1/sessions/create ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\":\"%user_id%\"}" > session.json

# Extract session_id (use PowerShell for easier JSON parsing)
```

### Pattern 2: Maintain Conversation Context

```bash
# Message 1
curl -X POST http://localhost:8000/api/v1/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"session_id\":\"sess-123\",\"message\":\"Hello\"}"

# Message 2 (same session = maintains context)
curl -X POST http://localhost:8000/api/v1/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"session_id\":\"sess-123\",\"message\":\"Tell me more\"}"
```

### Pattern 3: Retrieve History

```bash
# Get all messages
curl -X GET "http://localhost:8000/api/v1/chat/history/sess-123"

# Get with pagination
curl -X GET "http://localhost:8000/api/v1/chat/history/sess-123?limit=20&offset=0"
curl -X GET "http://localhost:8000/api/v1/chat/history/sess-123?limit=20&offset=20"
```

---

**Ready to test!** Start the server and try these examples.
