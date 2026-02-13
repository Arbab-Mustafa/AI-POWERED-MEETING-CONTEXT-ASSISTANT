# Quick Start Development Guide (30 Minutes Total)

## Prerequisites Checklist

Before starting development, you need:

- [x] Backend folder created ✅
- [x] Frontend folder created ✅
- [x] Python virtual environment created ✅
- [ ] Free PostgreSQL database (3 min) ⏱️
- [ ] Environment variables configured (25 min) ⏱️
- [ ] Dependencies installed (5 min) ⏱️

---

## Fast Track Setup (Follow in Order)

### Phase 1: Database Setup (3 minutes)
📄 **Follow:** `FREE_POSTGRES_SETUP.md`

1. Go to https://neon.tech
2. Sign up with Google
3. Create project: `contextmeet-db`
4. Copy connection string
5. Add to `backend/.env`:
   ```env
   DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
   DATABASE_ASYNC_URL=postgresql+asyncpg://user:pass@host/db?sslmode=require
   ```

✅ **Done? Continue to Phase 2**

---

### Phase 2: Essential Environment Variables (15 minutes)

Create `backend/.env` file with these values:

```env
# Security (REQUIRED - 1 minute)
SECRET_KEY=your-super-secret-key-min-32-chars-use-random-string-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database (REQUIRED - from Phase 1)
DATABASE_URL=postgresql://...
DATABASE_ASYNC_URL=postgresql+asyncpg://...

# Google OAuth (REQUIRED - 10 minutes)
# Get from: https://console.cloud.google.com/apis/credentials
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/callback

# Gmail Notifications (OPTIONAL - 3 minutes)
# Get from: https://myaccount.google.com/apppasswords
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx

# Telegram Notifications (OPTIONAL - 2 minutes)
# Get from: https://t.me/BotFather
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# AI Model (REQUIRED - 10 minutes for first-time install)
MISTRAL_BASE_URL=http://localhost:11434

# Environment Settings
ENVIRONMENT=development
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000
LOG_LEVEL=INFO
SENTRY_DSN=
```

**Where to get these values:**
- `SECRET_KEY`: Generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `GOOGLE_CLIENT_ID/SECRET`: See `ENV_SETUP_GUIDE.txt` (Section 3)
- `GMAIL_APP_PASSWORD`: See `ENV_SETUP_GUIDE.txt` (Section 4)
- `TELEGRAM_BOT_TOKEN`: See `ENV_SETUP_GUIDE.txt` (Section 5)

---

### Phase 3: Frontend Environment Variables (1 minute)

Create `frontend/.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
NEXT_PUBLIC_APP_NAME=ContextMeet
NEXT_PUBLIC_APP_VERSION=1.0.0
```

**Note:** Use the SAME `GOOGLE_CLIENT_ID` from backend/.env

---

### Phase 4: Install Ollama + Mistral Model (10 minutes for first-time)

**Windows:**
```powershell
# Download Ollama
# Go to: https://ollama.ai/download
# Click "Download for Windows"
# Run the installer (OllamaSetup.exe)

# After installation, open PowerShell and run:
ollama pull mistral

# Verify installation:
ollama list
# You should see: mistral:latest
```

**Keep Ollama running in the background** (it starts automatically after install)

---

### Phase 5: Install Dependencies (5 minutes)

**Backend Dependencies:**
```powershell
# Activate virtual environment
cd backend
.\venv\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; print('FastAPI installed:', fastapi.__version__)"
```

**Frontend Dependencies:**
```powershell
# In new terminal
cd frontend

# Install packages
npm install

# Verify installation
npm list --depth=0
```

---

## Start Development (3 Terminal Windows)

### Terminal 1: Ollama Service
```powershell
ollama serve
# Should show: "Ollama is running on http://localhost:11434"
# Keep this terminal open
```

### Terminal 2: Backend API
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Should show:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

Test backend: http://localhost:8000/health

### Terminal 3: Frontend Dev Server
```powershell
cd frontend
npm run dev

# Should show:
# ready - started server on 0.0.0.0:3000
# Local: http://localhost:3000
```

Open browser: http://localhost:3000

---

## Minimal Setup (Skip Optional Services)

If you want to start coding IMMEDIATELY, use this minimal `.env`:

```env
# backend/.env (MINIMAL - only what's needed to run)
SECRET_KEY=dev-secret-key-only-for-local-testing-min-32-chars-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
DATABASE_ASYNC_URL=postgresql+asyncpg://user:pass@host/db?sslmode=require

GOOGLE_CLIENT_ID=get-from-google-cloud-console.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=get-from-google-cloud-console
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/callback

MISTRAL_BASE_URL=http://localhost:11434

ENVIRONMENT=development
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000
LOG_LEVEL=INFO

# Skip these for now (add later when needed):
# GMAIL_EMAIL=
# GMAIL_APP_PASSWORD=
# TELEGRAM_BOT_TOKEN=
# SENTRY_DSN=
```

**You can add Gmail and Telegram later when you implement notifications.**

---

## What to Do Next

After servers are running, you can start building:

### Backend Development (API Routes)
1. Create `backend/app/controllers/` folder
2. Add route files:
   - `auth_controller.py` (login, register, OAuth)
   - `meeting_controller.py` (CRUD for meetings)
   - `context_controller.py` (AI brief generation)
   - `notification_controller.py` (send notifications)
3. Register routes in `main.py`

### Frontend Development (UI Components)
1. Create components in `frontend/src/components/`
2. Build pages in `frontend/src/app/`
3. Connect to API using `src/services/api.ts`

---

## Development Workflow

```
┌─────────────────────────────────────────┐
│  User opens http://localhost:3000       │
│  (Next.js Frontend)                     │
└────────────────┬────────────────────────┘
                 │
                 │ API calls
                 ▼
┌─────────────────────────────────────────┐
│  Backend API http://localhost:8000      │
│  (FastAPI + SQLAlchemy)                 │
└────────┬──────────────────┬─────────────┘
         │                  │
         │                  │ AI requests
         ▼                  ▼
┌─────────────────┐  ┌──────────────────┐
│  Neon Database  │  │  Ollama Mistral  │
│  (PostgreSQL)   │  │  localhost:11434 │
└─────────────────┘  └──────────────────┘
```

---

## Troubleshooting

### "Command 'ollama' not found"
- Ollama not installed or not in PATH
- Restart PowerShell after installing Ollama
- Verify: `ollama --version`

### "Connection refused" on port 8000
- Backend not running
- Check terminal for errors
- Make sure virtual environment is activated

### "Module not found" errors
- Dependencies not installed
- Run `pip install -r requirements.txt` in backend
- Run `npm install` in frontend

### "Database connection failed"
- Check Neon dashboard - database might be paused
- Verify connection strings in `.env`
- Make sure both DATABASE_URL and DATABASE_ASYNC_URL are set

---

## Current Progress

✅ **Completed:**
- Backend architecture (Models, Schemas, Repositories, Services)
- Frontend architecture (Types, API client, State management)
- Project structure (21 folders, 30+ files)

⏱️ **Next: 30 minutes of setup**
1. Free database (3 min)
2. Environment variables (15 min)
3. Ollama install (10 min)
4. Dependencies install (5 min)

🚀 **Then: Start coding!**
- Build API controllers
- Build UI components
- Implement AI features
- Add Google Calendar integration

---

## Time Estimate Breakdown

| Task | Time | Skippable? |
|------|------|-----------|
| Neon database setup | 3 min | ❌ Required |
| Generate SECRET_KEY | 1 min | ❌ Required |
| Google OAuth setup | 10 min | ❌ Required |
| Gmail setup | 3 min | ✅ Optional |
| Telegram setup | 2 min | ✅ Optional |
| Ollama install | 10 min | ❌ Required |
| Backend dependencies | 3 min | ❌ Required |
| Frontend dependencies | 2 min | ❌ Required |
| **Total (all features)** | **34 min** | |
| **Total (minimal)** | **29 min** | Skip Gmail+Telegram |

---

## Ready to Start?

**Step 1:** Set up free database (`FREE_POSTGRES_SETUP.md`)  
**Step 2:** Configure environment variables (this guide)  
**Step 3:** Install Ollama + dependencies (this guide)  
**Step 4:** Start development servers (this guide)  
**Step 5:** Start coding! 🚀

**Questions? Check:**
- `ENV_SETUP_GUIDE.txt` - Detailed explanations
- `DETAILED_STEP_BY_STEP_SETUP.txt` - Command-by-command walkthrough
- `QUICK_REFERENCE.txt` - Printable checklist

---

**Let's build ContextMeet!** 🎯
