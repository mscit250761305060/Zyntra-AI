# Complete Setup Instructions

## System Requirements

- Windows/Linux/macOS
- Python 3.14+
- MySQL 8.0+
- 500MB disk space
- Google Gemini API Key

## Step-by-Step Installation

### Step 1: Verify Python Installation

```powershell
python --version  # Should be Python 3.14+
pip --version
```

### Step 2: Create Virtual Environment

```powershell
# Create
python -m venv .venv

# Activate
.\.venv\Scripts\Activate.ps1

# On Linux/macOS:
# source .venv/bin/activate
```

### Step 3: Upgrade pip

```bash
pip install --upgrade pip
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

**Installed Packages:**
- FastAPI - Web framework
- Uvicorn - ASGI server
- Google ADK - Multi-agent orchestration
- Pydantic - Data validation
- MySQL Connector - Database driver
- Python-dotenv - Environment variables

### Step 5: MySQL Setup

#### Option A: Using MySQL Workbench/Command Line

```sql
-- Create user (optional, if not using root)
CREATE USER 'chatbot'@'localhost' IDENTIFIED BY 'chatbot_password';
GRANT ALL PRIVILEGES ON chatbot_db.* TO 'chatbot'@'localhost';
FLUSH PRIVILEGES;

-- Database will be created automatically by init_database.py
```

#### Option B: Using Docker (Alternative)

```powershell
docker run --name mysql_chatbot -e MYSQL_ROOT_PASSWORD=root -p 3306:3306 -d mysql:8.0
```

### Step 6: Configure Environment Variables

**Create `.env` file:**

```bash
cp .env.example .env
```

**Edit `.env`:**

```env
# Required: Get from Google Cloud Console
GEMINI_API_KEY=sk-proj-xxxxxxxxxxxxx

# MySQL Configuration
MYSQL_HOST=localhost           # or your-server.com
MYSQL_PORT=3306               # Default MySQL port
MYSQL_USER=root               # Your MySQL username
MYSQL_PASSWORD=your_password  # Your MySQL password
MYSQL_DATABASE=chatbot_db     # Database name

# MySQL Connection Pool
MYSQL_POOL_SIZE=5             # Number of connections
MYSQL_POOL_NAME=chatbot_pool
MYSQL_POOL_RESET_SESSION=True

# Application Settings
APP_NAME=Zyntra AI
APP_ENV=development           # development or production
DEBUG=True                    # False in production
LOG_LEVEL=INFO                # DEBUG, INFO, WARNING, ERROR

# Server
SERVER_HOST=0.0.0.0          # All interfaces
SERVER_PORT=8000             # Port number
RELOAD=True                  # Auto-reload on file changes

# Sessions
SESSION_TIMEOUT_MINUTES=30
MAX_SESSIONS_PER_USER=10

# Default User ID
DEFAULT_USER_ID=default_user
```

### Step 7: Verify Database Connection

Test MySQL connection:

```powershell
# Using Python
python -c "
import mysql.connector
from src.core.config import settings

try:
    conn = mysql.connector.connect(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
    )
    print('✓ MySQL connection successful!')
    conn.close()
except Exception as e:
    print(f'✗ MySQL connection failed: {e}')
"
```

### Step 8: Initialize Database

Run the database initialization script:

```bash
python -m scripts.init_database
```

**Expected Output:**
```
2026-06-23 10:00:00 [INFO] chatbot.db_init: Starting database initialization...
2026-06-23 10:00:00 [INFO] chatbot.db_init: MySQL Configuration: localhost:3306/chatbot_db
2026-06-23 10:00:00 [INFO] chatbot.db_init: Database 'chatbot_db' created or already exists
2026-06-23 10:00:00 [INFO] chatbot.db_init: Table 'users' created or already exists
2026-06-23 10:00:00 [INFO] chatbot.db_init: Table 'sessions' created or already exists
2026-06-23 10:00:00 [INFO] chatbot.db_init: Table 'messages' created or already exists
...
2026-06-23 10:00:00 [INFO] chatbot.db_init: Database initialization completed successfully
```

### Step 9: Start the Application

```bash
python main.py
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 10: Verify Installation

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"ok","message":"Zyntra AI is running","version":"1.0.0"}
```

## API Documentation

Once running, access:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## Directory Structure After Setup

```
d:\chatbot\code\
├── .venv/                     # Virtual environment
├── .env                       # Environment variables (CREATED)
├── .env.example               # Template (provided)
├── logs/                      # Logs directory (auto-created)
│   ├── chatbot.log           # General logs
│   └── chatbot_error.log     # Error logs
├── scripts/
│   └── init_database.py      # Database setup
├── src/                       # Source code
│   ├── agents/               # ADK agents
│   ├── api/                  # API layer
│   ├── core/                 # Core utilities
│   ├── models/               # Data models
│   ├── repositories/         # Data access
│   └── utils/                # Utilities
├── main.py                   # Main application
├── requirements.txt          # Dependencies
├── pyproject.toml           # Project config
├── README.md                # Full documentation
├── QUICKSTART.md            # Quick start
└── SETUP.md                 # This file
```

## Verify All Components

### Check Python Environment

```powershell
python -c "
import sys
import pkg_resources

print(f'Python: {sys.version}')
print(f'Location: {sys.executable}')
print()
print('Key Packages:')
for pkg in ['fastapi', 'google-adk', 'mysql.connector', 'pydantic']:
    try:
        version = pkg_resources.get_distribution(pkg).version
        print(f'  ✓ {pkg}: {version}')
    except:
        print(f'  ✗ {pkg}: NOT INSTALLED')
"
```

### Check Database

```powershell
python -c "
from src.repositories.user_repository import user_repository
from src.repositories.session_repository import session_repository
from src.repositories.message_repository import message_repository

print('✓ User Repository: OK')
print('✓ Session Repository: OK')
print('✓ Message Repository: OK')
print()
print('All components initialized successfully!')
"
```

### Check API Routes

```bash
curl http://localhost:8000/api/v1/info
```

## MySQL Table Verification

Connect to MySQL and verify:

```sql
USE chatbot_db;

-- List all tables
SHOW TABLES;

-- Expected output:
-- +-------------------------+
-- | Tables_in_chatbot_db    |
-- +-------------------------+
-- | agent_interactions      |
-- | audit_logs              |
-- | conversation_metadata   |
-- | messages                |
-- | sessions                |
-- | users                   |
-- +-------------------------+

-- Verify structure
DESCRIBE users;
DESCRIBE sessions;
DESCRIBE messages;
```

## Testing the Complete System

### 1. Create a Session

```bash
$session = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/sessions/create" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body (@{user_id="test-user"; title="Test Session"} | ConvertTo-Json)

$session_id = $session.Content | ConvertFrom-Json | Select-Object -ExpandProperty session_id
Write-Host "Created session: $session_id"
```

### 2. Send a Message

```bash
$response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/chat" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body (@{session_id=$session_id; message="What is Python?"} | ConvertTo-Json)

$response.Content | ConvertFrom-Json | Select-Object response
```

### 3. Get History

```bash
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/chat/history/$session_id" `
  | Select-Object -ExpandProperty Content `
  | ConvertFrom-Json
```

## Troubleshooting

### Issue: ModuleNotFoundError: No module named 'src'

**Solution:**
```bash
# Ensure you're in project root
cd d:\chatbot\code

# Reinstall in editable mode
pip install -e .

# Or add to Python path
$env:PYTHONPATH = "$env:PYTHONPATH;d:\chatbot\code"
```

### Issue: MySQL Connection Refused

**Solution:**
```bash
# Check MySQL is running
# Windows:
Get-Service MySQL80  # or your MySQL service name

# Linux:
sudo systemctl status mysql

# Verify credentials in .env match your MySQL setup
```

### Issue: GEMINI_API_KEY not found

**Solution:**
1. Verify .env file exists in project root
2. Check GEMINI_API_KEY is set
3. No spaces around `=` in .env:
   ```env
   GEMINI_API_KEY=sk-proj-xxx  # ✓ Correct
   GEMINI_API_KEY = sk-proj-xxx # ✗ Wrong
   ```

### Issue: Port 8000 already in use

**Solution:**
```bash
# Use different port
uvicorn main:app --port 8001

# Or kill process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

## Next Steps

1. ✅ Installation complete
2. 📖 Read: README.md for full documentation
3. 🚀 Run: `python main.py`
4. 📚 Explore: http://localhost:8000/api/docs
5. 🧪 Test: Send messages and check history
6. 🔧 Customize: Add your own agents and tools

## Production Checklist

- [ ] Set `DEBUG=False` in .env
- [ ] Set `LOG_LEVEL=WARNING` in .env
- [ ] Use strong MySQL password
- [ ] Enable MySQL SSL
- [ ] Configure CORS origins
- [ ] Set up database backups
- [ ] Configure log rotation
- [ ] Use HTTPS
- [ ] Set up monitoring/alerting
- [ ] Load test the system

## Support Resources

- **API Documentation**: http://localhost:8000/api/docs
- **Error Logs**: `logs/chatbot_error.log`
- **Configuration**: `.env` file
- **Database**: MySQL `chatbot_db`
- **Main Application**: `main.py`

---

**Installation Complete!** 🎉

You're ready to start building with the Zyntra AI!
