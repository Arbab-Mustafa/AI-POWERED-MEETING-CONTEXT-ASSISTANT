# ContextMeet Frontend

AI-Powered Meeting Context Assistant - Frontend Application

## Overview

This is the Next.js frontend for ContextMeet, a web application that helps users prepare for meetings by automatically generating AI-powered context, syncing with Google Calendar, and sending smart notifications.

## Tech Stack

- **Framework**: Next.js 16.1.6 (App Router)
- **Language**: TypeScript 5.3.3
- **Styling**: Tailwind CSS 3.3.6
- **State Management**: Zustand 4.4.2
- **HTTP Client**: Axios 1.13.5
- **Form Handling**: React Hook Form 7.48.0
- **Validation**: Zod 3.22.4
- **Date/Time**: date-fns 2.30.0

## Project Structure

```
frontend/src/
├── app/                    # Next.js App Router pages
│   ├── page.tsx           # Home page with auth redirect
│   ├── login/             # Login page
│   ├── register/          # Registration page
│   ├── dashboard/         # Main dashboard
│   ├── meetings/          # Meeting pages
│   │   ├── page.tsx      # All meetings list
│   │   ├── new/          # Create meeting form
│   │   └── [id]/         # Meeting detail page
│   ├── settings/          # User settings
│   └── profile/           # User profile
├── services/
│   └── api.ts            # API client with all endpoints
├── store/
│   ├── auth.ts           # Authentication state
│   ├── meetings.ts       # Meeting management state
│   └── contexts.ts       # AI context state
├── types/
│   └── index.ts          # TypeScript interfaces
└── styles/
    └── globals.css       # Global Tailwind styles
```

## Features Implemented

### Authentication
- ✅ Email/password registration with validation
- ✅ Login with JWT token management
- ✅ Auto-redirect based on auth state
- ✅ Session persistence via localStorage
- ✅ Google OAuth button (placeholder)
- ✅ Profile management page

### Meeting Management
- ✅ Create meetings with full details
- ✅ View all meetings with filtering
- ✅ Search meetings by title/description
- ✅ Individual meeting detail page
- ✅ Google Calendar sync button
- ✅ Edit and delete meetings

### AI Context Generation
- ✅ Auto-generate AI context for meetings
- ✅ Manual regenerate with force option
- ✅ Display AI brief, key topics, checklist
- ✅ Interactive checklist completion
- ✅ Attendee insights display

### Dashboard
- ✅ Today's meetings section
- ✅ Upcoming meetings list
- ✅ Quick stats and actions
- ✅ Google Calendar sync
- ✅ AI Ready badges

## Getting Started

### Installation

```bash
cd frontend
npm install
```

### Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Build for Production

```bash
npm run build
npm start
```

## Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## API Integration

All 51 backend endpoints integrated:
- Auth API (6 endpoints)
- Meetings API (8 endpoints)
- Context API (6 endpoints)
- Notifications API (7 endpoints)

See `src/services/api.ts` for details.

## State Management

### Auth Store
```typescript
{
  token, user, isAuthenticated
  login(), register(), logout()
}
```

### Meeting Store
```typescript
{
  meetings, currentMeeting, isLoading
  fetchMeetings(), createMeeting(), updateMeeting()
}
```

### Context Store
```typescript
{
  contexts, isGenerating
  fetchContext(), generateContext()
}
```

## User Flow

1. Register/Login → Dashboard
2. Create Meeting → Auto-generate AI context
3. View Meeting Details → See AI preparation
4. Configure Settings → Notifications & Calendar

## Design System

- **Colors**: Purple-Blue gradient theme
- **Typography**: Tailwind font system
- **Components**: Card-based layouts
- **Responsive**: Mobile-first design

## Testing with Backend

1. Start backend: `uvicorn app.main:app --reload`
2. Start frontend: `npm run dev`
3. Test complete flow: Register → Create Meeting → Generate AI Context

## License

MIT License
