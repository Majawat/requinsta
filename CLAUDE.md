# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Docker (Primary Development Method)
```bash
# Start the full application
docker-compose up

# Start with rebuild
docker-compose up --build

# Access database directly
docker compose exec db psql -U requinsta -d requinsta

# Make first user admin (if needed)
docker compose exec db psql -U requinsta -d requinsta -c "UPDATE users SET role = 'ADMIN' WHERE email = 'your@email.com';"
```

### Frontend (Vue.js + Vite)
```bash
cd frontend
npm run dev        # Development server
npm run build      # Production build
npm run preview    # Preview production build
```

### Backend (FastAPI + SQLAlchemy)
```bash
cd backend
uvicorn app.main:app --reload  # Development server
# Or use the Docker setup which includes auto-reload
```

## Architecture Overview

### High-Level Structure
- **Frontend**: Vue 3 + Vite + Tailwind CSS + Pinia state management
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL + Alembic migrations
- **Deployment**: Docker Compose with hot-reload for development

### Key Design Patterns

#### Plugin System
The application uses a modular plugin architecture for metadata providers:
- Base classes in `backend/app/plugins/base.py`
- Concrete implementations like `openlibrary.py` 
- Plugins implement `MetadataProvider` interface with `search()` and `get_by_id()` methods
- Plugin manager handles discovery and routing

#### State Management (Frontend)
- **Pinia stores** for global state:
  - `auth.js`: Authentication, user session, token management
  - `requests.js`: Media requests CRUD operations
- API communication through axios with automatic token injection
- Dynamic API URL construction based on hostname

#### Backend Architecture
- **FastAPI router structure** with versioned API (`/api/v1/`)
- **SQLAlchemy models** with enums for type safety:
  - `MediaType`: book, audiobook, movie, tv_show, music, comic, other
  - `RequestStatus`: PENDING, APPROVED, FULFILLED, DENIED
  - `UserRole`: ADMIN, MODERATOR, POWER_USER, USER, READ_ONLY
- **Alembic migrations** for database schema changes
- **JWT authentication** with role-based access control

### Database Schema
- **Users**: email, password_hash, role, timestamps
- **Requests**: user_id, title, description, media_type, status, timestamps
- Foreign key relationships maintained through SQLAlchemy

### Frontend Components
- **Role-based UI**: Admin vs regular user layouts
- **Dark theme**: Pre-configured with Tailwind dark mode
- **Responsive design**: Mobile-first approach with Tailwind utilities
- **Component structure**: LoginForm, RequestForm, AdminPanel, UserManagement

## Development URLs
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

## Media Types Supported
The system supports universal media types through the `MediaType` enum:
book, audiobook, movie, tv_show, music, comic, other

## Role System
Five-tier role system: ADMIN → MODERATOR → POWER_USER → USER → READ_ONLY