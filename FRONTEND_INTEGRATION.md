# Frontend Integration Guide

## Overview

The chatbot now includes a modern, responsive web frontend that's fully integrated with the FastAPI backend. No separate frontend server needed - everything runs from one Python application.

## Architecture

```
FastAPI Server
├── API Routes (/api/v1/*)
├── Static Files (/static/*)
│   └── index.html (Frontend UI)
├── Auto Docs (/api/docs)
└── Health Check (/health)
```

## Frontend Features

✨ **User-Friendly Interface**
- Clean, modern chat UI
- Message history display
- Real-time message updates
- Session management
- Responsive design (works on mobile)

🎯 **Core Features**
- User identification (saved in localStorage)
- Multiple chat sessions
- Session history
- Message timestamps
- Status indicators
- Error handling

🛠️ **Technical Stack**
- Vanilla JavaScript (no frameworks required)
- CSS3 with animations
- Responsive design
- Local storage for persistence
- Fetch API for backend communication

## Running the Application

### Method 1: Automatic (Recommended)
```bash
python run.py
```

### Method 2: Manual
```bash
python main.py
```

### Method 3: Using Uvicorn
```bash
uvicorn main:app --reload
```

## Accessing the Frontend

Once the server is running, open your browser to:

**Frontend**: http://localhost:8000/static/index.html
**API Docs**: http://localhost:8000/api/docs
**Health Check**: http://localhost:8000/health

## Frontend Workflow

### 1. Initial Load
- User enters their name (saved in localStorage)
- Frontend loads user's existing sessions

### 2. Starting a Chat
- Click "New Chat" button
- Enter session title
- Session is created and ready for messages

### 3. Sending Messages
- Type message in input field
- Press Enter or click Send
- Message displayed with timestamp
- API processes message
- Response displayed as assistant message

### 4. Session Management
- Click any session in sidebar to switch
- Sessions are listed with titles
- Click "Clear All" to delete all sessions

## API Integration

The frontend communicates with these endpoints:

### Sessions
```javascript
// Create session
POST /api/v1/sessions/create
Body: { user_id: string }

// Get user sessions
GET /api/v1/sessions/user/{user_id}

// Update session
PUT /api/v1/sessions/{session_id}
Body: { title: string }

// Delete session
DELETE /api/v1/sessions/{session_id}

// Get session history
GET /api/v1/chat/history/{session_id}
```

### Chat
```javascript
// Send message
POST /api/v1/chat
Body: {
  user_id: string,
  session_id: string,
  message: string
}
Response: { response: string }
```

## Frontend File Structure

```
src/
└── static/
    └── index.html (600+ lines)
        ├── HTML structure
        ├── Embedded CSS (600+ lines)
        ├── JavaScript logic (400+ lines)
        └── API communication
```

## Customization

### Change Color Theme
Edit the CSS gradient colors in `src/static/index.html`:

```css
body {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.btn {
    background: #667eea;
}
```

### Change App Title
Edit the header section:
```html
<h1>🤖 Zyntra AI</h1>
<p>Your custom subtitle here</p>
```

### Modify Message Styling
Edit the `.message-content` CSS class to change message appearance.

## How User Data is Stored

### Frontend (Browser)
- User ID saved in localStorage
- User name saved in localStorage
- Messages kept in memory during session
- No persistent data in browser (except user ID)

### Backend (Server)
- Sessions saved to `data/sessions.json`
- Messages saved to `data/messages.json`
- User info saved to `data/users.json`
- All data persisted automatically

## Security Considerations

### Frontend
- No sensitive data in localStorage (only user ID)
- No API keys exposed
- CORS configured in FastAPI

### Backend
- Environment variables for secrets (in .env)
- Input validation on all endpoints
- Error messages don't leak sensitive info

### For Production
- Update `allow_origins=["*"]` in main.py to specific domains
- Add authentication if needed
- Enable HTTPS
- Set `DEBUG=false` in .env

## Browser Compatibility

✅ Chrome/Edge (latest)
✅ Firefox (latest)
✅ Safari (latest)
✅ Mobile browsers

## Troubleshooting

### Frontend not loading?
```bash
# Check if static files are mounted
curl http://localhost:8000/static/index.html

# Check main.py logs
# Should show: "Static files mounted from ..."
```

### Messages not sending?
1. Open browser DevTools (F12)
2. Check Console tab for errors
3. Check Network tab for API requests
4. Ensure backend is running: http://localhost:8000/health

### Sessions not appearing?
1. Check `data/sessions.json` file
2. Verify user ID is same across requests
3. Check browser console for errors

### CORS errors?
- Already configured in main.py
- If issues persist, check that endpoints are correct
- Verify API is running on localhost:8000

## Testing the Integration

### 1. Test API Directly
```bash
# Create session
curl -X POST http://localhost:8000/api/v1/sessions/create \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user"}'

# Send message
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "session_id": "session_id",
    "message": "Hello"
  }'
```

### 2. Test Frontend
1. Open http://localhost:8000/static/index.html
2. Enter name and start chat
3. Type message and send
4. Check that response appears

### 3. Verify Data Persistence
1. Send a message
2. Refresh the page
3. Verify message history still appears
4. Check `data/messages.json`

## Deployment

### For Production Hosting

1. **Local Development**
   ```bash
   python main.py
   ```

2. **Production Server** (using Gunicorn)
   ```bash
   pip install gunicorn
   gunicorn main:app -w 4 -b 0.0.0.0:8000
   ```

3. **Docker** (if needed)
   ```dockerfile
   FROM python:3.11
   WORKDIR /app
   COPY . .
   RUN pip install -r requirements.txt
   CMD ["python", "main.py"]
   ```

## Next Steps

1. ✅ Run the app: `python run.py`
2. ✅ Open frontend: http://localhost:8000/static/index.html
3. ✅ Start chatting
4. ✅ Check API docs: http://localhost:8000/api/docs
5. ✅ Monitor data: Check `data/` folder

## Frontend Screenshot

The interface includes:
- **Header**: Title and description
- **Sidebar**: Session list and controls
- **Chat Area**: Messages with timestamps
- **Input Field**: Message input with send button
- **Modal Dialogs**: For user name and session creation
- **Status Messages**: For feedback and errors

All with smooth animations and responsive design!

---

**Status**: ✨ Frontend fully integrated and ready to use!
