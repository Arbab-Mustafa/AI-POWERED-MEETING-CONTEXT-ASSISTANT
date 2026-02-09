ContextMeet - AI-Powered Meeting Context Assistant

Project Structure:

- backend/ - Python FastAPI backend
- frontend/ - Next.js React frontend

QUICK START:

Backend Setup:

1. cd backend
2. python -m venv venv
3. Activate venv: venv\Scripts\activate (Windows) or source venv/bin/activate (Mac/Linux)
4. pip install -r requirements.txt
5. cp .env.example .env
6. python -m app.main

Frontend Setup:

1. cd frontend
2. npm install
3. cp .env.example .env.local
4. npm run dev

Access:

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
