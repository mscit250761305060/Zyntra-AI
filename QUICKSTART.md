# Quick Start Guide

## Setup (One-Time)

### 1. Activate Virtual Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure .env

```bash
# Copy template
cp .env.example .env

# Edit .env with your values
# - GEMINI_API_KEY
# - MySQL connection details
```

### 4. Initialize Database

```bash
python -m scripts.init_database
```

## Running

### Start the Server

```bash
python main.py
```

Server starts at: **http://localhost:8000**

### Access API Documentation

Open in browser:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## Quick API Test

### 1. Create a Session

```bash
curl -X POST http://localhost:8000/api/v1/sessions/create \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "title": "My Chat Session"
  }'
```

**Response:**
```json
{
  "session_id": "abc-123-xyz",
  "user_id": "user-123",
  "title": "My Chat Session",
  "created_at": "2026-06-23T10:00:00",
  "is_active": true
}
```

### 2. Send a Message

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc-123-xyz",
    "message": "How do I write a Python function?",
    "user_id": "user-123"
  }'
```

**Response:**
```json
{
  "response": "To write a Python function, you can...",
  "session_id": "abc-123-xyz"
}
```

### 3. Get Chat History

```bash
curl http://localhost:8000/api/v1/chat/history/abc-123-xyz
```

### 4. Get User Sessions

```bash
curl http://localhost:8000/api/v1/sessions/user/user-123
```

## Common Commands

```bash
# Run with auto-reload
python main.py

# Run with specific port
uvicorn main:app --port 8001

# Initialize DB only
python -m scripts.init_database

# View logs
type logs\chatbot.log

# View error logs
type logs\chatbot_error.log
```

## Directory Structure

```
d:\chatbot\code\
├── main.py                 # Start here
├── requirements.txt        # Install: pip install -r requirements.txt
├── .env                    # Configure: Copy from .env.example
├── .env.example           # Template for .env
├── README.md              # Full documentation
├── QUICKSTART.md          # This file
├── scripts/
│   └── init_database.py   # Run: python -m scripts.init_database
├── src/
│   ├── agents/            # ADK agents
│   ├── api/               # FastAPI routes, controllers, services
│   ├── core/              # Config, database
│   ├── models/            # Database models, schemas
│   ├── repositories/      # Data layer
│   └── utils/             # Logging, helpers
└── logs/                  # Application logs (auto-created)
```

## Database Setup

### Automatic (Recommended)

```bash
python -m scripts.init_database
```

### Manual MySQL Commands

```sql
-- Create database
CREATE DATABASE IF NOT EXISTS chatbot_db;

-- Use database
USE chatbot_db;

-- Then run init_database.py to create tables
```

## Troubleshooting

### Port 8000 Already In Use

```bash
# Use different port
uvicorn main:app --port 8001
```

### MySQL Connection Error

1. Check MySQL is running
2. Verify credentials in `.env`:
   ```env
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=your_password
   MYSQL_DATABASE=chatbot_db
   ```

### Import Errors

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### API Returns 500 Error

1. Check logs: `type logs\chatbot_error.log`
2. Verify `.env` configuration
3. Ensure database is initialized

## API Quick Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check |
| GET | `/api/docs` | API documentation |
| POST | `/api/v1/sessions/create` | Create session |
| GET | `/api/v1/sessions/{id}` | Get session details |
| GET | `/api/v1/sessions/user/{user_id}` | List user sessions |
| PUT | `/api/v1/sessions/{id}` | Update session |
| DELETE | `/api/v1/sessions/{id}` | Delete session |
| POST | `/api/v1/chat` | Send message |
| GET | `/api/v1/chat/history/{id}` | Get message history |

## Next Steps

1. ✅ Setup complete
2. Run: `python main.py`
3. Go to: http://localhost:8000/api/docs
4. Test endpoints using Swagger UI
5. Build your app!

## Need Help?

- API Docs: http://localhost:8000/api/docs
- Full Guide: See README.md
- Error Logs: Check `logs/chatbot_error.log`
- Config: Edit `.env` file
