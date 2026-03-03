# Research-Oriented SaaS Data Analytics Platform (Phase 1)

Backend foundation for a multi-tenant SaaS platform using FastAPI + PostgreSQL.

This phase implements:
- JWT authentication
- Role-Based Access Control (Admin, Researcher, Viewer)
- Multi-tenant organization structure
- Secure password hashing with passlib + bcrypt
- PostgreSQL integration via SQLAlchemy
- Alembic migration workflow

No analytics, ML, datasets, or subscriptions are included in this phase.

## Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy 2.x
- PostgreSQL
- Alembic
- passlib[bcrypt]
- python-jose (JWT)

## Project Structure

```text
app/
+-- main.py
+-- core/
¦   +-- config.py
¦   +-- security.py
+-- db/
¦   +-- session.py
¦   +-- base.py
+-- models/
¦   +-- organization.py
¦   +-- user.py
+-- schemas/
¦   +-- auth.py
¦   +-- user.py
+-- api/
¦   +-- deps.py
¦   +-- routes/
¦       +-- auth.py
¦       +-- users.py
+-- services/

alembic/
+-- env.py
+-- versions/
    +-- 0001_initial_schema.py
```

## Environment Variables

Create a `.env` file from the example:

```powershell
copy .env.example .env
```

Required values:

```env
DATABASE_URL=postgresql://ai_analytics_user:YOUR_PASSWORD@localhost:5432/ai_analytics_saas
SECRET_KEY=your_long_random_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

If your DB password contains special characters (`@`, `#`, etc.), URL-encode it in `DATABASE_URL`.

Example:
- raw password: `@lphaBetaSaasAi@#008`
- encoded password: `%40lphaBetaSaasAi%40%23008`

## Local Setup

1. Create virtual environment

```powershell
python -m venv .venv
```

2. Activate virtual environment (PowerShell)

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies

```powershell
pip install -e .
```

4. Ensure bcrypt compatibility for passlib

```powershell
python -m pip install --upgrade --force-reinstall bcrypt==4.0.1
```

## Database Migrations

Run all migrations:

```powershell
alembic upgrade head
```

Rollback to base if needed:

```powershell
alembic downgrade base
```

Create a new migration after model changes:

```powershell
alembic revision --autogenerate -m "your message"
```

## Run the API

```powershell
uvicorn app.main:app --reload
```

- Base URL: `http://127.0.0.1:8000`
- Swagger Docs: `http://127.0.0.1:8000/docs`
- Health check: `GET /health`

## API Endpoints (Phase 1)

### Auth
- `POST /api/v1/auth/register`
  - Body: `email`, `password`, `full_name`, `organization_name`
  - Behavior:
    - Creates organization if it does not exist
    - First user in organization becomes `Admin`
    - Returns JWT access token

- `POST /api/v1/auth/login`
  - Body: `email`, `password`
  - Returns JWT access token

### Users
- `GET /api/v1/users/me`
  - Requires Bearer token
  - Returns currently authenticated user

- `GET /api/v1/users`
  - Admin only
  - Returns users in the same organization

- `PUT /api/v1/users/{id}`
  - Admin only
  - Update user role and/or activation status

- `DELETE /api/v1/users/{id}`
  - Admin only
  - Soft delete via `is_active=false`

## Authentication in Swagger

1. Call `POST /api/v1/auth/login`.
2. Copy `access_token` from response.
3. Click **Authorize** in Swagger.
4. Paste token as:

```text
Bearer <access_token>
```

Leave `client_id` and `client_secret` empty.

## Error Handling

Structured JSON responses with relevant status codes:
- `400` invalid input
- `401` authentication failure
- `403` unauthorized role/access
- `404` resource not found

## Notes

- Email is globally unique.
- Every user belongs to exactly one organization.
- Organization-level isolation is enforced in user-management logic.
- Passwords are hashed and never returned by API responses.
- bcrypt has a 72-byte input limit; API validates and rejects overly long passwords.

## Git Push Checklist

Before pushing:

1. Ensure `.env` is not committed.
2. Run migration status check:

```powershell
alembic current
```

3. Start server and sanity-check:
- `/health`
- `/docs`
- register -> login -> `/users/me`

4. Commit:

```powershell
git add .
git commit -m "phase1: backend foundation with auth, rbac, multitenancy, migrations"
git push
```
