# Quick Start - File-Based Persistence (No MySQL Required)

This chatbot now includes **file-based persistence** that works without MySQL. Sessions and messages are saved to JSON files in the `data/` directory.

## Installation

1. **Install dependencies** (without MySQL):
```bash
pip install -r requirements.txt
```

2. **Copy .env template**:
```bash
# On Windows
copy .env.example .env

# On Linux/Mac
cp .env.example .env
```

3. **Update .env** (optional - defaults work):
```env
GEMINI_API_KEY=your_api_key_here
APP_ENV=development
DEBUG=true
```

## Running the Application

```bash
python main.py
```

The API will be available at: **http://localhost:8000**
- API Docs: http://localhost:8000/api/docs
- Health Check: http://localhost:8000/health

## Data Storage

All data is saved to JSON files in the `data/` directory:
- `data/users.json` - User accounts
- `data/sessions.json` - Chat sessions
- `data/messages.json` - Messages by session

To reset all data, delete the `data/` folder and restart the app.

## Testing

### Using the Web UI (Swagger)
Visit http://localhost:8000/api/docs and use the interactive API documentation.

### Using cURL

#### 1. Create a session:
```bash
curl -X POST http://localhost:8000/api/v1/sessions/create \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123"}'
```

#### 2. Send a message:
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "session_id": "session_id_from_above",
    "message": "What is Python?"
  }'
```

#### 3. Get session history:
```bash
curl http://localhost:8000/api/v1/chat/history/session_id_from_above
```

## Migrating to MySQL

When you're ready to use MySQL:

1. **Uncomment MySQL in requirements.txt** and reinstall:
```bash
pip install mysql-connector-python>=8.0.33
```

2. **Start MySQL server** and ensure it's running on localhost:3306

3. **Update .env** with MySQL credentials:
```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=yourpassword
MYSQL_DATABASE=chatbot_db
```

4. **Initialize the database**:
```bash
python -m scripts.init_database
```

5. **Update repository imports** to use MySQL instead of file persistence.

## Features

✅ Multi-agent chatbot with Google ADK  
✅ File-based session and message persistence  
✅ FastAPI REST API with automatic documentation  
✅ No external dependencies for data storage  
✅ Easy migration to MySQL when needed  
✅ Rotating file-based logging  

## Troubleshooting

**Port 8000 already in use?**
```bash
# Use a different port
uvicorn main:app --host 0.0.0.0 --port 8001
```

**Data not persisting?**
- Check that the `data/` folder exists and is writable
- Check logs in the `logs/` folder

**API not responding?**
- Ensure `GEMINI_API_KEY` is set in `.env`
- Check the logs: `tail -f logs/chatbot.log`

## Next Steps

- Check the API documentation: http://localhost:8000/api/docs
- Read [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for architecture details
- Read [API_TESTING.md](API_TESTING.md) for more testing examples
