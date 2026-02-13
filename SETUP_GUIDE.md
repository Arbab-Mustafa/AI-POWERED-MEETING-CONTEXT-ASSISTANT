# ContextMeet - Complete Setup & Testing Guide

## 🎯 Overview

This guide will help you set up and test the complete ContextMeet application (backend + frontend).

## 📋 Prerequisites

- Python 3.9+ installed
- Node.js 18+ installed
- PostgreSQL 12+ installed and running
- Git installed
- Ollama installed (for AI context generation) - Optional but recommended

## 🚀 Quick Start

### 1. Database Setup

Create PostgreSQL database:

```sql
CREATE DATABASE contextmeet;
CREATE USER contextmeet_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE contextmeet TO contextmeet_user;
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from template)
cp .env.example .env

# Edit .env with your database credentials
# Required:
# DATABASE_URL=postgresql+asyncpg://contextmeet_user:your_password@localhost/contextmeet
# SECRET_KEY=your-secret-key-here (generate with: openssl rand -hex 32)

# Initialize database
python -m app.db.init_db

# Start backend server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://localhost:8000**  
API docs at: **http://localhost:8000/docs**

### 3. Frontend Setup

Open a new terminal:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env.local file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local

# Start development server
npm run dev
```

Frontend will be available at: **http://localhost:3000**

### 4. Ollama Setup (Optional - for AI Features)

Install Ollama from: https://ollama.ai

```bash
# Pull Mistral model
ollama pull mistral

# Verify it's running
ollama list
```

## ✅ Testing the Application

### Automated API Tests

Run the test script to verify all backend endpoints:

```bash
# From project root directory
python test_api.py
```

This will test:
- ✅ User registration
- ✅ User login
- ✅ JWT authentication
- ✅ Meeting creation
- ✅ Meeting listing

### Manual Frontend Testing

1. **Open browser**: http://localhost:3000

2. **Register a new account**:
   - Click "Create one"
   - Fill in email, name, password
   - Click "Register"
   - Should auto-redirect to dashboard

3. **Create a meeting**:
   - Click "New Meeting" button
   - Fill in:
     - Title: "Team Sync"
     - Description: "Weekly team synchronization meeting"
     - Start time: Tomorrow at 10:00 AM
     - End time: Tomorrow at 11:00 AM
     - Attendees: colleague@example.com
     - Enable "Auto-generate AI Context"
   - Click "Create Meeting"

4. **View meeting details**:
   - Click on the created meeting
   - Should see meeting information
   - Should see AI-generated context (if Ollama is running)
   - Try checking off preparation checklist items

5. **Test Google Calendar Sync**:
   - Click "Sync Calendar" button on dashboard
   - (Requires Google OAuth setup)

6. **Test Settings**:
   - Click "Settings" in quick actions
   - Configure notification preferences
   - Save settings

### Verify Database

Check that data is being saved:

```sql
-- Connect to PostgreSQL
psql -U contextmeet_user -d contextmeet

-- Check users
SELECT id, email, name, created_at FROM users;

-- Check meetings
SELECT id, title, start_time, context_generated FROM meetings;

-- Check contexts
SELECT id, meeting_id, meeting_type, confidence_score FROM contexts;
```

## 🔧 Troubleshooting

### Backend Issues

#### Issue: "Cannot connect to database"
**Solution**:
- Verify PostgreSQL is running: `pg_isready`
- Check DATABASE_URL in .env
- Ensure database exists: `psql -l | grep contextmeet`

#### Issue: "ModuleNotFoundError"
**Solution**:
```bash
cd backend
pip install -r requirements.txt
```

#### Issue: "Ollama connection failed"
**Solution**:
- Install Ollama: https://ollama.ai
- Pull Mistral model: `ollama pull mistral`
- Verify: `ollama list`
- Make sure Ollama service is running

### Frontend Issues

#### Issue: "Cannot connect to API"
**Solution**:
- Verify backend is running on port 8000
- Check .env.local has correct API URL
- Check browser console for CORS errors

#### Issue: "Module not found"
**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### Issue: "Port 3000 already in use"
**Solution**:
```bash
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti :3000 | xargs kill
```

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user

### Meetings
- `GET /api/v1/meetings` - List all meetings
- `POST /api/v1/meetings` - Create meeting
- `GET /api/v1/meetings/{id}` - Get meeting details
- `PUT /api/v1/meetings/{id}` - Update meeting
- `DELETE /api/v1/meetings/{id}` - Delete meeting
- `POST /api/v1/meetings/sync/google` - Sync Google Calendar

### AI Context
- `GET /api/v1/contexts/meeting/{meeting_id}` - Get meeting context
- `POST /api/v1/contexts/generate` - Generate AI context
- `PUT /api/v1/contexts/{id}` - Update context
- `DELETE /api/v1/contexts/{id}` - Delete context

### Notifications
- `GET /api/v1/notifications` - List notifications
- `POST /api/v1/notifications` - Schedule notification
- `POST /api/v1/notifications/auto-schedule/{meeting_id}` - Auto-schedule
- `DELETE /api/v1/notifications/{id}` - Cancel notification

Full API documentation: http://localhost:8000/docs

## 🎨 Feature Checklist

### Backend ✅
- [x] User authentication (JWT)
- [x] Meeting CRUD operations
- [x] AI context generation (Mistral)
- [x] Google Calendar sync
- [x] Email notifications
- [x] Telegram notifications
- [x] Database models & migrations
- [x] Repository pattern
- [x] Service layer
- [x] Error handling

### Frontend ✅
- [x] User registration/login
- [x] Dashboard with stats
- [x] Meeting list & filters
- [x] Create meeting form
- [x] Meeting detail page
- [x] AI context display
- [x] Interactive checklist
- [x] Settings page
- [x] Profile page
- [x] Responsive design
- [x] Loading states
- [x] Error handling

## 🔐 Security Notes

1. **Change SECRET_KEY**: Generate a secure key for production
   ```bash
   openssl rand -hex 32
   ```

2. **Database Credentials**: Use strong passwords in production

3. **CORS Settings**: Update allowed origins in production

4. **Environment Variables**: Never commit .env files

5. **API Keys**: Store Google OAuth credentials securely

## 📈 Performance Tips

1. **Database Indexing**: Already configured on key fields
2. **Connection Pooling**: Configured in database settings
3. **Async Operations**: All I/O is asynchronous
4. **Caching**: Consider Redis for production
5. **Frontend**: Use production build for deployment

## 🚢 Production Deployment

### Backend
```bash
# Build
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Or use Docker
docker build -t contextmeet-backend .
docker run -p 8000:8000 contextmeet-backend
```

### Frontend
```bash
# Build for production
npm run build

# Start production server
npm start

# Or use Docker
docker build -t contextmeet-frontend .
docker run -p 3000:3000 contextmeet-frontend
```

## 📞 Support

For issues or questions:
1. Check the logs: Backend terminal and browser console
2. Review this guide thoroughly
3. Check API documentation at /docs
4. Verify all prerequisites are installed

## 🎉 Success Criteria

Your setup is complete when:
- ✅ Backend starts without errors on port 8000
- ✅ Frontend starts without errors on port 3000
- ✅ You can register a new user
- ✅ You can login and see the dashboard
- ✅ You can create a meeting
- ✅ AI context generates (if Ollama is set up)
- ✅ Test script passes all checks

Congratulations! Your ContextMeet application is ready to use! 🎊
