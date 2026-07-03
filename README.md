# Zyntra AI

A production-ready multi-agent chatbot system powered by Google ADK and FastAPI. 

> **NEW**: File-based persistence system - no MySQL setup required! Start in seconds.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python run.py

# 3. Open browser to http://localhost:8000/api/docs
```

**That's it!** Data is automatically saved to `data/` folder as JSON files.

For detailed setup guide, see [QUICKSTART_FILEBASED.md](QUICKSTART_FILEBASED.md).

## Features

✅ **Multi-Agent Architecture**
- Main orchestrator agent that intelligently routes requests
- 4 specialized sub-agents: Coder, Planner, Researcher, Summarizer
- Single-turn and multi-turn conversation support

✅ **Session Management**
- User-wise isolated chat sessions
- Persistent session and message storage (file-based or MySQL)
- Conversation history retrieval
- Session metadata tracking

✅ **Persistence Options**
- **File-Based** (Default) - JSON files in `data/` folder, no setup needed
- **MySQL** (Optional) - Full database support for production

✅ **REST API**
- FastAPI with automatic documentation
- Chat endpoints with message history
- Session management (create, read, update, delete)
- Comprehensive error handling

✅ **Production Ready**
- Type hints throughout
- Comprehensive logging
- Environment variable configuration
- Error handling and validation

## Architecture

```
Zyntra AI
├── main.py                          # FastAPI application
├── src/
│   ├── agents/                      # ADK agents configuration
│   │   ├── main_agent/
│   │   │   └── agent.py             # Main orchestrator agent
│   │   ├── sub_agents/
│   │   │   ├── coding_agent.py      # Coding specialist
│   │   │   ├── planner_agent.py     # Planning specialist
│   │   │   ├── research_agent.py    # Research specialist
│   │   │   └── summarizer_agent.py  # Summarization specialist
│   │   ├── tools/
│   │   │   ├── calculator_tool.py   # Math tool
│   │   │   └── search_tool.py       # Search tool (optional)
│   │   ├── prompts/
│   │   │   └── system_prompt.py     # System prompts
│   │   ├── runner/
│   │   │   └── chatbot_runner.py    # ADK runner setup
│   │   └── sessions/
│   │       └── session_manager.py   # Session management
│   ├── api/
│   │   ├── controllers/             # Request handlers
│   │   │   ├── chat_controller.py   # Chat controller
│   │   │   └── session_controller.py # Session controller
│   │   ├── services/                # Business logic
│   │   │   ├── chat_service.py      # Chat processing
│   │   │   └── session_service.py   # Session operations
│   │   └── routes/                  # API endpoints
│   │       ├── chat_routes.py       # Chat endpoints
│   │       └── session_routes.py    # Session endpoints
│   ├── core/
│   │   ├── config.py                # Configuration
│   │   └── database.py              # Database connection
│   ├── models/
│   │   ├── database_models.py       # Database models
│   │   ├── schemas.py               # Pydantic schemas
│   │   └── ...
│   ├── repositories/                # Data access layer
│   │   ├── user_repository.py       # User operations
│   │   ├── session_repository.py    # Session operations
│   │   └── message_repository.py    # Message operations
│   └── utils/
│       ├── logger.py                # Logging configuration
│       └── helpers.py               # Helper functions
├── scripts/
│   └── init_database.py             # Database initialization
├── requirements.txt                  # Python dependencies
├── pyproject.toml                   # Project configuration
├── .env.example                     # Environment variables template
└── README.md                        # This file
```

## Installation

### Prerequisites

- Python 3.14+
- MySQL 8.0+
- Google Gemini API Key

### Step 1: Clone/Setup Project

```bash
cd d:\chatbot\code
```

### Step 2: Create Virtual Environment

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

Copy `.env.example` to `.env` and update with your settings:

```bash
cp .env.example .env
```

Edit `.env` with:
- Your Google Gemini API Key
- MySQL connection details
- Other configuration as needed

Example `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=chatbot_db

APP_ENV=development
DEBUG=True
LOG_LEVEL=INFO
```

### Step 5: Initialize Database

Run the database initialization script:

```bash
python -m scripts.init_database
```

This will:
1. Create the MySQL database if it doesn't exist
2. Create all required tables with proper schema
3. Set up indexes and constraints

**SQL Tables Created:**
- `users` - User accounts
- `sessions` - Chat sessions
- `messages` - Conversation messages
- `conversation_metadata` - Session statistics
- `agent_interactions` - Agent tracking
- `audit_logs` - System audit trail

### Step 6: Run the Application

```bash
# Development mode with auto-reload
python main.py

# Or use uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **Application**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## API Endpoints

### Health & Info

```http
GET /health
GET /
GET /api/v1/info
```

### Chat Endpoints

```http
POST /api/v1/chat
Get request body:
{
  "session_id": "session-123",
  "message": "What is machine learning?",
  "user_id": "user-456"  # Optional
}

Response:
{
  "response": "Machine learning is...",
  "session_id": "session-123"
}

---

GET /api/v1/chat/history/{session_id}?limit=50&offset=0
Response:
{
  "session_id": "session-123",
  "messages": [
    {
      "id": 1,
      "session_id": "session-123",
      "role": "user",
      "content": "...",
      "created_at": "2026-06-23T10:00:00"
    },
    ...
  ],
  "count": 50
}
```

### Session Endpoints

```http
POST /api/v1/sessions/create
{
  "user_id": "user-123",
  "title": "Coding Help",
  "description": "Python debugging session"
}

Response:
{
  "session_id": "abc-123-def",
  "user_id": "user-123",
  "created_at": "2026-06-23T10:00:00",
  "is_active": true
}

---

GET /api/v1/sessions/{session_id}
Response:
{
  "session_id": "abc-123",
  "user_id": "user-123",
  "title": "Coding Help",
  "message_count": 15,
  "created_at": "2026-06-23T10:00:00",
  "is_active": true
}

---

GET /api/v1/sessions/user/{user_id}
Response:
{
  "user_id": "user-123",
  "sessions": [...],
  "count": 5
}

---

PUT /api/v1/sessions/{session_id}
{
  "title": "New Title",
  "description": "Updated description"
}

---

DELETE /api/v1/sessions/{session_id}
Response:
{
  "message": "Session deleted successfully",
  "session_id": "abc-123"
}

---

GET /api/v1/sessions/{session_id}/history?limit=50&offset=0
Response:
{
  "session_id": "abc-123",
  "messages": [...],
  "count": 50,
  "limit": 50,
  "offset": 0
}

---

DELETE /api/v1/sessions/{session_id}/history
Response:
{
  "message": "Session history cleared",
  "session_id": "abc-123",
  "messages_deleted": 42
}
```

## How It Works

### 1. Chat Flow

```
User Request
    ↓
POST /api/v1/chat
    ↓
ChatController.chat()
    ↓
ChatService.chat()
    ├─ Load/Create session
    ├─ Save user message to MySQL
    ├─ Load conversation history
    ├─ Invoke ADK Runner
    │   ├─ Main Agent receives message
    │   ├─ Determines which sub-agent to use:
    │   │  ├─ Coding? → CodingAgent
    │   │  ├─ Planning? → PlannerAgent
    │   │  ├─ Research? → ResearchAgent
    │   │  └─ Summary? → SummarizerAgent
    │   └─ Returns response
    ├─ Save agent response to MySQL
    └─ Return response to user
```

### 2. Agent Routing

The main agent intelligently routes requests based on keywords and context:

- **Coding Agent**: code, programming, debug, refactor, function, class, method
- **Planner Agent**: plan, schedule, organize, outline, checklist, project, timeline
- **Research Agent**: research, analyze, find, search, learn, understand, explore
- **Summarizer Agent**: summarize, summary, condense, brief, extract, overview

### 3. Session Management

```
Session Lifecycle:
Create Session
    ↓
Initialize in MySQL & ADK
    ↓
User sends messages
    ↓
Messages persisted to MySQL
    ↓
History retrieved on demand
    ↓
Session deleted (removes all data)
```

### 4. Message Persistence

Every message is stored with:
- Content
- Role (user, assistant)
- Agent name (for agent responses)
- Timestamp
- Metadata (optional)
- Message type

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Sessions Table
```sql
CREATE TABLE sessions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    app_name VARCHAR(100),
    title VARCHAR(500),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_accessed_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
```

### Messages Table
```sql
CREATE TABLE messages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    message_id VARCHAR(255) UNIQUE,
    role VARCHAR(50) NOT NULL,  -- user, assistant, chatbot
    content LONGTEXT NOT NULL,
    agent_name VARCHAR(100),
    message_type VARCHAR(50),   -- text, tool_call, tool_response
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
```

### Other Tables
- `conversation_metadata` - Session statistics
- `agent_interactions` - Agent execution tracking
- `audit_logs` - System audit trail

## Configuration

### Environment Variables

```env
# Google Gemini
GEMINI_API_KEY=sk-...

# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DATABASE=chatbot_db
MYSQL_POOL_SIZE=5

# Application
APP_NAME=Zyntra AI
APP_ENV=development
DEBUG=True
LOG_LEVEL=INFO

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
RELOAD=True

# Sessions
SESSION_TIMEOUT_MINUTES=30
MAX_SESSIONS_PER_USER=10

# Default User
DEFAULT_USER_ID=default_user
```

## Logging

Logs are stored in the `logs/` directory:
- `chatbot.log` - General application logs
- `chatbot_error.log` - Error logs only

Log level can be configured via `LOG_LEVEL` environment variable (DEBUG, INFO, WARNING, ERROR, CRITICAL).

## Project Structure

### Layer-based Architecture

1. **API Layer** (`src/api/`)
   - Routes: Define HTTP endpoints
   - Controllers: Handle HTTP requests
   - Services: Business logic
   - Schemas: Request/response validation

2. **Agent Layer** (`src/agents/`)
   - Main agent with sub-agents
   - Google ADK runner and session management
   - Tools for agent capabilities

3. **Data Layer** (`src/repositories/`)
   - User operations
   - Session operations
   - Message operations
   - Database abstraction

4. **Core Layer** (`src/core/`)
   - Configuration management
   - Database connection and pooling
   - Shared utilities

### Separation of Concerns

- **Controllers**: Only handle HTTP request/response transformation
- **Services**: Contain business logic and orchestration
- **Repositories**: Handle all database operations
- **Agents**: Pure ADK configuration

## Advanced Usage

### Custom Sub-Agents

Add new sub-agents in `src/agents/sub_agents/`:

```python
from google.adk.agents import Agent

my_custom_agent = Agent(
    name="my_agent",
    description="Description of what this agent does",
    model="gemini-2.5-flash-lite",
    instruction="Custom system instructions...",
    mode="single_turn",
)
```

Then add to main agent in `src/agents/main_agent/agent.py`:

```python
chatbot_agent = Agent(
    ...
    sub_agents=[..., my_custom_agent],
)
```

### Custom Tools

Add tools in `src/agents/tools/`:

```python
def my_tool(param: str) -> str:
    """Tool description."""
    # Implementation
    return result
```

Add to main agent:

```python
chatbot_agent = Agent(
    ...
    tools=[calculator, my_tool],
)
```

### Query History by Role

```python
# Get all user messages
user_messages = message_repository.get_session_messages(
    session_id, 
    limit=100
)
user_only = [m for m in user_messages if m['role'] == 'user']
```

## Troubleshooting

### MySQL Connection Error

```
Error: MySQL Connection Failed
```

**Solution:**
1. Verify MySQL is running
2. Check connection credentials in `.env`
3. Ensure database exists or run `init_database.py`

### Import Errors

```
ModuleNotFoundError: No module named 'src'
```

**Solution:**
1. Ensure you're running from project root
2. Check `.env` is in project root
3. Verify virtual environment is activated

### No Responses from Agent

Check:
1. GEMINI_API_KEY is valid
2. Agent routing keywords match user input
3. View logs in `logs/` directory

## Production Deployment

### Pre-deployment Checklist

- [ ] Update `.env` with production values
- [ ] Set `DEBUG=False`
- [ ] Set `LOG_LEVEL=WARNING`
- [ ] Use strong MySQL password
- [ ] Enable HTTPS
- [ ] Configure CORS origins
- [ ] Set up database backups
- [ ] Configure logging rotation
- [ ] Test all endpoints

### Docker Deployment

```dockerfile
FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

## Performance Optimization

### Database

- Connection pooling enabled (configured via `MYSQL_POOL_SIZE`)
- Indexes on frequently queried columns
- Message pagination (limit 1000)

### Caching

- ADK in-memory session service for current session
- MySQL for long-term persistence

### Scalability

- Stateless API design
- Database-backed sessions (shareable across instances)
- Connection pooling for concurrent requests

## Contributing

To extend the system:

1. Add new agents in `src/agents/sub_agents/`
2. Add new tools in `src/agents/tools/`
3. Add new API endpoints in `src/api/routes/`
4. Add business logic in `src/api/services/`

## License

MIT

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review API documentation at `http://localhost:8000/api/docs`
3. Check `.env` configuration

---

**Version**: 1.0.0  
**Created**: 2026-06-23  
**Last Updated**: 2026-06-23
