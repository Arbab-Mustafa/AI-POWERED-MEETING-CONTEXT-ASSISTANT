<<<<<<< HEAD
# ContextMeet - AI-Powered Meeting Context Assistant
=======
 ContextMeet - AI-Powered Meeting Context Assistant
>>>>>>> ebbda7fcd4c30b3bf25f24455b574093dcb329a2

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16+-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3+-blue.svg)](https://www.typescriptlang.org/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

ContextMeet is an intelligent meeting management system that uses AI to automatically generate meeting preparation context, sync with Google Calendar, and send smart notifications via Email and Telegram.

## ✨ Features

### 🤖 AI-Powered Context Generation
- Automatic meeting analysis using Mistral 7B
- Smart meeting type classification
- Key topics extraction
- Personalized preparation checklists
- Attendee insights and recommendations

### 📅 Calendar Integration
- Google Calendar sync
- Automatic meeting import
- Two-way synchronization
- Multi-calendar support

### 🔔 Smart Notifications
- Email reminders
- Telegram notifications
- WhatsApp integration (planned)
- Customizable reminder timing
- Do-not-disturb mode

### 💼 Meeting Management
- Create, read, update, delete meetings
- Rich meeting details (attendees, links, notes)
- Meeting status tracking
- Search and filter functionality

### 🎨 Modern UI
- Responsive design (mobile, tablet, desktop)
- Beautiful gradient theme
- Interactive dashboards
- Real-time updates
- Loading states and error handling

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 12+
- Ollama (optional, for AI features)

### Option 1: Quick Start Scripts (Windows)

```bash
# Start backend
start-backend.bat

# Start frontend (in new terminal)
start-frontend.bat
```

### Option 2: Manual Setup

#### Backend Setup

#### Backend Setup

```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your database credentials

# Initialize database
python -m app.db.init_db

# Start server
python -m uvicorn app.main:app --reload
```

Backend runs at: **http://localhost:8000**  
API docs at: **http://localhost:8000/docs**

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Setup environment
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local

# Start development server
npm run dev
```

Frontend runs at: **http://localhost:3000**

## 📖 Documentation

- **[Setup Guide](SETUP_GUIDE.md)** - Complete installation and configuration
- **[Bug Fixes](BUGFIX_SUMMARY.md)** - Recent fixes and improvements
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs
- **[Backend README](backend/README.md)** - Backend architecture details
- **[Frontend README](frontend/README.md)** - Frontend architecture details

## 🧪 Testing

### Run Automated Tests

```bash
# Test all backend API endpoints
python test_api.py
```

### Manual Testing

1. Open http://localhost:3000
2. Register a new account
3. Create a meeting
4. Generate AI context
5. View dashboard and explore features

## 🏗️ Architecture

### Backend Stack
- **Framework**: FastAPI (async Python web framework)
- **Database**: PostgreSQL with asyncpg
- **ORM**: SQLAlchemy 2.0 (async)
- **AI**: Ollama + Mistral 7B
- **Auth**: JWT tokens
- **Email**: SMTP (Gmail)
- **Telegram**: python-telegram-bot

### Frontend Stack
- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript 5.3
- **Styling**: Tailwind CSS 3.3
- **State**: Zustand 4.4
- **HTTP**: Axios 1.13
- **Forms**: React Hook Form + Zod
- **Dates**: date-fns 2.30

### Project Structure

```
ContextMeet/
├── backend/
│   ├── app/
│   │   ├── controllers/      # API endpoints
│   │   ├── services/         # Business logic
│   │   ├── repositories/     # Data access
│   │   ├── models/           # Database models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── core/             # Config & utilities
│   │   └── db/               # Database setup
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js pages
│   │   ├── services/         # API client
│   │   ├── store/            # State management
│   │   └── types/            # TypeScript types
│   ├── package.json
│   └── README.md
├── test_api.py
├── start-backend.bat
├── start-frontend.bat
├── SETUP_GUIDE.md
└── README.md
```

## 🔑 Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/contextmeet
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI (Optional)
OLLAMA_API_URL=http://localhost:11434
AI_MODEL=mistral

# Email (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Telegram (Optional)
TELEGRAM_BOT_TOKEN=your-bot-token
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user

### Meetings
- `GET /api/v1/meetings` - List meetings
- `POST /api/v1/meetings` - Create meeting
- `GET /api/v1/meetings/{id}` - Get meeting
- `PUT /api/v1/meetings/{id}` - Update meeting
- `DELETE /api/v1/meetings/{id}` - Delete meeting
- `POST /api/v1/meetings/sync/google` - Sync calendar

### AI Context
- `GET /api/v1/contexts/meeting/{meeting_id}` - Get context
- `POST /api/v1/contexts/generate` - Generate context
- `PUT /api/v1/contexts/{id}` - Update context
- `DELETE /api/v1/contexts/{id}` - Delete context

### Notifications
- `GET /api/v1/notifications` - List notifications
- `POST /api/v1/notifications` - Schedule notification
- `POST /api/v1/notifications/auto-schedule/{meeting_id}` - Auto-schedule
- `DELETE /api/v1/notifications/{id}` - Cancel notification

## 🎯 Development Status

- [x] User authentication & authorization
- [x] Meeting CRUD operations
- [x] AI context generation
- [x] Google Calendar sync
- [x] Email notifications
- [x] Telegram notifications
- [x] Frontend dashboard
- [x] Responsive design
- [x] Error handling
- [ ] Learning system & analytics
- [ ] Mobile app (planned)

## 🔧 Troubleshooting

### Backend won't start
- Check PostgreSQL is running
- Verify DATABASE_URL in .env
- Ensure all dependencies installed

### Frontend can't connect
- Verify backend is running on port 8000
- Check .env.local has correct API_URL
- Look for CORS errors in browser console

### AI context not generating
- Install Ollama: https://ollama.ai
- Pull Mistral model: `ollama pull mistral`
- Verify Ollama service is running

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed troubleshooting.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 👨‍💻 Author

Built with ❤️ for better meeting preparation

---

**Status**: Production Ready ✅  
**Last Updated**: February 14, 2026  
**Version**: 1.0.0

- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

ARCHITECTURE:

Backend:

- Framework: FastAPI
- Database: PostgreSQL (Supabase)
- Style: Component-based MVC
- AI: Mistral 7B via Ollama
- Max file size: 500-700 lines

Frontend:

- Framework: Next.js 14
- Styling: Tailwind CSS
- State: Zustand
- Language: TypeScript
- Design: Light, professional, no emoji

DEVELOPMENT WORKFLOW:

1. Create feature branch: git checkout -b feature/feature-name
2. Make changes following architecture guidelines
3. Commit with clear messages
4. Push and create pull request
5. Code review before merge

CODE STANDARDS:

Backend:

- Type hints on all functions
- Docstrings for modules and classes
- PEP 8 compliance
- Async-first design
- Error handling with logging

Frontend:

- TypeScript strict mode
- React hooks best practices
- Proper key props in lists
- No console.log in production
- Accessibility considerations

DEPLOYMENT:

Backend: Railway.app (free tier)
Frontend: Vercel (free tier)

See individual README files for detailed setup instructions.



