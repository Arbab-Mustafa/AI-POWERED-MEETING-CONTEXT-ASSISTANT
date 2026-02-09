BACKEND - ContextMeet API

Architecture: Component-based with MVC pattern
Language: Python 3.11+
Framework: FastAPI + Uvicorn

FOLDER STRUCTURE:

app/
core/ - Configuration, database setup
models/ - SQLAlchemy database models
schemas/ - Pydantic validation schemas
repositories/ - Data access layer (DAO pattern)
services/ - Business logic layer
controllers/ - HTTP endpoint handlers
agents/ - Multi-agent system
utils/ - Helpers and utilities
middleware/ - Custom middleware
main.py - FastAPI app initialization

tests/ - Unit and integration tests
requirements.txt - Python dependencies
.env.example - Environment variables template

SETUP INSTRUCTIONS:

1. Create virtual environment:
   python -m venv venv
2. Activate virtual environment:
   Windows: venv\Scripts\activate
   Mac/Linux: source venv/bin/activate

3. Install dependencies:
   pip install -r requirements.txt

4. Configure environment:
   cp .env.example .env
   Edit .env with your credentials

5. Run development server:
   python -m app.main

API will be available at: http://localhost:8000
Documentation at: http://localhost:8000/docs

ARCHITECTURE PRINCIPLES:

1. Separation of Concerns
   - Models: Data definition only
   - Repositories: Data access only
   - Services: Business logic only
   - Controllers: HTTP handling only

2. Component-Based
   - Each component has single responsibility
   - Max 500-700 lines per file
   - Clear interfaces between components

3. Type Safety
   - Full type hints on all functions
   - Pydantic schemas for validation
   - SQLAlchemy models for database

4. Async-First
   - All database operations async
   - Support for background tasks
   - Non-blocking I/O throughout

5. Error Handling
   - Custom exceptions
   - Proper logging
   - Consistent error responses

KEY FILES:

core/config.py - Settings, database initialization
models/db.py - All SQLAlchemy models
schemas/base.py - All Pydantic schemas
repositories/base.py - All data access objects
services/base.py - All business logic
main.py - FastAPI app setup
