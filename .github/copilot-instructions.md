# ContextMeet - AI Coding Agent Instructions

## Project Overview
ContextMeet is an AI-powered meeting context assistant with FastAPI backend and Next.js frontend. The system integrates Google Calendar, generates AI meeting briefs using Mistral, and sends notifications via Email/Telegram.

## Architecture Principles

### Backend: Strict Layered Architecture (DO NOT VIOLATE)
```
Controllers → Services → Repositories → Models
```

**Critical Rules:**
- **Controllers**: HTTP handling only. No business logic, no direct DB access
- **Services**: Business logic only. Coordinate between repos and external APIs
- **Repositories**: Data access only (DAO pattern). Pure CRUD operations
- **Models**: SQLAlchemy ORM definitions only. No methods beyond `__repr__`

**File Size Limit**: Maximum 500-700 lines per file. Split into submodules if exceeded.

**Example Pattern** (see [backend/app/controllers/meeting_controller.py](backend/app/controllers/meeting_controller.py)):
```python
@router.post("/meetings")
async def create_meeting(
    meeting_data: MeetingCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Controller delegates to service
    calendar_service = CalendarService(db)
    meeting = await calendar_service.create_meeting(current_user.id, meeting_data)
    return MeetingResponse.from_orm(meeting)
```

### Frontend: App Router + Zustand State Management

**Structure:**
- Pages: `frontend/src/app/*/page.tsx` (Next.js App Router)
- API Client: Single centralized instance in [frontend/src/services/api.ts](frontend/src/services/api.ts)
- State: Zustand stores in [frontend/src/store/](frontend/src/store/) (auth, meetings, contexts)
- Types: Shared interfaces in [frontend/src/types/index.ts](frontend/src/types/index.ts)

**State Pattern** (see [frontend/src/store/meetings.ts](frontend/src/store/meetings.ts)):
```typescript
export const useMeetingStore = create<MeetingState>((set, get) => ({
  meetings: [],
  isLoading: false,
  error: null,
  fetchMeetings: async () => {
    set({ isLoading: true });
    const data = await meetingsAPI.list();
    set({ meetings: data, isLoading: false });
  }
}));
```

## Development Workflows

### Starting the Application
**Windows (Recommended):**
```bash
# Terminal 1: Backend
start-backend.bat

# Terminal 2: Frontend  
start-frontend.bat
```

**Manual:**
```bash
# Backend (requires venv activation)
cd backend
venv\Scripts\activate  # Windows
python -m uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev
```

### Database Initialization
```bash
cd backend
python -m app.db.init_db  # Creates all tables from SQLAlchemy models
```

### Testing API Endpoints
- Interactive docs: `http://localhost:8000/docs` (Swagger UI)
- Test script: [test_api.py](test_api.py) - Manual API testing
- Test services: [backend/test_services.py](backend/test_services.py)

## Key Conventions

### Environment Variables (Critical)
Both backend and frontend are **heavily environment-dependent**:
- **Backend**: 12+ required vars (database, Google OAuth, Telegram, Gmail, AI model URL)
- **Frontend**: API URL, timeouts
- See [ENV_SETUP_GUIDE.txt](ENV_SETUP_GUIDE.txt) and [ENV_VISUAL_GUIDE.txt](ENV_VISUAL_GUIDE.txt)
- Examples: [ENV_FILLED_EXAMPLES.txt](ENV_FILLED_EXAMPLES.txt)

**Never hardcode:**
- Database credentials
- API keys (Google, Telegram, Mistral)
- Email credentials
- Frontend API URLs

### Async-First Backend
**All database operations must be async:**
```python
# ✅ Correct
async def get_user(user_id: UUID, db: AsyncSession):
    user_repo = UserRepository(db)
    return await user_repo.get_by_id(user_id)

# ❌ Wrong - synchronous DB call
def get_user_sync(user_id: UUID, db: Session):
    return db.query(User).filter(User.id == user_id).first()
```

### Type Safety Requirements
- **Backend**: Full type hints on all functions (enforced)
- **Frontend**: TypeScript strict mode (no `any` unless unavoidable)
- **API Contracts**: Pydantic schemas for validation (see [backend/app/schemas/base.py](backend/app/schemas/base.py))

### Database Models vs Schemas
- **Models** ([backend/app/models/db.py](backend/app/models/db.py)): SQLAlchemy ORM for database tables
- **Schemas** ([backend/app/schemas/base.py](backend/app/schemas/base.py)): Pydantic for API validation
  - `*Create`: Request payload
  - `*Update`: Partial update payload  
  - `*Response`: API response (uses `from_attributes = True`)

### Authentication Pattern
```python
# Dependency injection for protected routes
from app.controllers.auth_controller import get_current_user, get_db

@router.get("/protected")
async def protected_route(
    current_user = Depends(get_current_user),  # Auto JWT validation
    db: AsyncSession = Depends(get_db)
):
    # current_user is User object, already authenticated
    return {"user_id": current_user.id}
```

### Frontend API Client Pattern
Centralized axios instance with auto token injection (see [frontend/src/services/api.ts](frontend/src/services/api.ts)):
```typescript
// ✅ Use predefined API functions
import { meetingsAPI } from "@/services/api";
const meetings = await meetingsAPI.list();

// ❌ Don't create new axios instances
const response = await axios.get("http://localhost:8000/api/v1/meetings");
```

Token is automatically injected via interceptor; managed by `apiClient.setToken()`.

## Integration Points

### Google Calendar Sync
- Service: [backend/app/services/google_calendar.py](backend/app/services/google_calendar.py)
- OAuth tokens stored in `User.google_token` (encrypted)
- Sync triggered via `/meetings/sync/google` endpoint

### AI Context Generation
- Service: [backend/app/services/ai_service.py](backend/app/services/ai_service.py)  
- Uses Mistral 7B via Ollama (local) or API
- Generates: `ai_brief`, `key_topics`, `preparation_checklist`, `attendee_context`
- Model URL: `MISTRAL_BASE_URL` env var (default: `http://localhost:11434`)

### Notification Delivery
- Service: [backend/app/services/notification_delivery.py](backend/app/services/notification_delivery.py)
- Channels: Email (Gmail SMTP), Telegram Bot API
- Scheduled via `Notification` model with retry logic

## Common Patterns

### Creating New Endpoints
1. Define Pydantic schema in [backend/app/schemas/base.py](backend/app/schemas/base.py)
2. Add repository method in [backend/app/repositories/base.py](backend/app/repositories/base.py) (data access)
3. Add service method in [backend/app/services/base.py](backend/app/services/base.py) (business logic)
4. Add controller route in [backend/app/controllers/](backend/app/controllers/) (HTTP handler)
5. Register router in [backend/app/main.py](backend/app/main.py) if new controller

### Error Handling
```python
# Services raise business exceptions
if not user:
    raise ValueError("User with this email already exists")

# Controllers convert to HTTP exceptions
try:
    user = await auth_service.create_user(user_data)
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
```

### Frontend Loading States
```typescript
// Always use store loading states
const { isLoading, error } = useMeetingStore();

if (isLoading) return <LoadingSpinner />;
if (error) return <ErrorMessage message={error} />;
```

## Project-Specific Quirks

1. **Dual database URLs**: Both sync (`DATABASE_URL`) and async (`DATABASE_ASYNC_URL`) needed
2. **Soft deletes**: Users have `deleted_at` column (never hard delete)
3. **Meeting ownership**: Always verify `meeting.user_id == current_user.id` 
4. **Context auto-generation**: Triggered on meeting creation if attendees exist
5. **Timezone handling**: User timezones stored, all DB times in UTC
6. **Google Calendar event_id**: Used for deduplication during sync

## Documentation Resources
- **Setup**: [SETUP_GUIDE.md](SETUP_GUIDE.md), [START_HERE_SETUP_SUMMARY.txt](START_HERE_SETUP_SUMMARY.txt)
- **Backend Architecture**: [backend/README.md](backend/README.md)
- **Frontend Architecture**: [frontend/README.md](frontend/README.md)
- **Quick Start**: [QUICK_START_DEVELOPMENT.md](QUICK_START_DEVELOPMENT.md)
- **Environment Setup**: [ENV_SETUP_GUIDE.txt](ENV_SETUP_GUIDE.txt), [ENV_VISUAL_GUIDE.txt](ENV_VISUAL_GUIDE.txt)

## When Adding Features
- Follow the layered architecture pattern strictly
- Add type hints (backend) and TypeScript types (frontend)
- Update relevant Zustand store if state changes
- Add environment variables to `.env.example`
- Keep files under 500-700 lines
- Use async/await for all DB operations
