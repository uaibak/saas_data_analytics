# Research-Oriented SaaS Data Analytics Platform (Phases 1-2)

FastAPI backend for a multi-tenant SaaS platform with JWT auth, RBAC, and dataset ingestion/metadata foundation.

Implemented:
- Phase 1: Authentication, authorization, organization multi-tenancy
- Phase 2: Dataset upload, storage, metadata extraction, preview, tenant isolation

Not included yet:
- Analytics workflows
- ML training/inference
- Subscriptions/billing

## Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy 2.x
- PostgreSQL
- Alembic
- passlib + bcrypt
- python-jose (JWT)
- pandas + openpyxl

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
¦   +-- dataset.py
¦   +-- dataset_column.py
+-- schemas/
¦   +-- auth.py
¦   +-- user.py
¦   +-- dataset.py
+-- api/
¦   +-- deps.py
¦   +-- routes/
¦       +-- auth.py
¦       +-- users.py
¦       +-- datasets.py
+-- services/
    +-- file_storage_service.py
    +-- dataset_service.py

alembic/
+-- versions/
    +-- 0001_initial_schema.py
    +-- 0002_datasets_metadata.py
```

## Environment Variables

Copy template:

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
STORAGE_ROOT=storage
MAX_UPLOAD_SIZE_MB=10
CATEGORICAL_UNIQUE_RATIO_THRESHOLD=0.05
```

If password has special chars, URL-encode it (for example `@` -> `%40`, `#` -> `%23`).

## Local Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
python -m pip install --upgrade --force-reinstall bcrypt==4.0.1
```

## Migrations

```powershell
alembic upgrade head
```

## Run Server

```powershell
uvicorn app.main:app --reload
```

- Base URL: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- Health: `GET /health`

## API Endpoints

### Auth
- `POST /api/v1/auth/register` (JSON)
- `POST /api/v1/auth/login` (JSON)
- `POST /api/v1/auth/token` (OAuth2 form; used by Swagger Authorize)

### Users
- `GET /api/v1/users/me` (Any authenticated user)
- `GET /api/v1/users` (Admin)
- `PUT /api/v1/users/{id}` (Admin)
- `DELETE /api/v1/users/{id}` (Admin, soft deactivate)

### Datasets
- `POST /api/v1/datasets/upload` (Admin, Researcher)
  - multipart form fields: `name`, `description`, `file`
  - accepted file types: `.csv`, `.xlsx`
  - max file size: `MAX_UPLOAD_SIZE_MB`
  - stored under: `storage/{organization_id}/{dataset_id}/filename`
  - extracts metadata: row count, column count, per-column type/missing/unique count

- `GET /api/v1/datasets` (All roles in same organization)
  - returns active datasets only

- `GET /api/v1/datasets/{dataset_id}/preview` (All roles in same organization)
  - query: `page` (default `1`), `page_size` (default `100`, max `1000`)
  - returns preview rows + column names/types + counts

- `DELETE /api/v1/datasets/{dataset_id}` (Admin)
  - soft delete only (`is_active=false`)
  - file is retained on disk

## Security and Isolation

- JWT required on protected routes
- RBAC enforced (Admin/Researcher/Viewer)
- Organization-based access isolation for users and datasets
- Strict file extension validation
- Upload-size enforcement (`413`)
- Sanitized filenames and controlled storage path

## Error Semantics

- `400` invalid input or unreadable dataset file
- `401` unauthorized
- `403` insufficient role
- `404` resource not found in tenant scope
- `413` payload too large

## Swagger Usage

### Option A (recommended)
1. Open `/docs`.
2. Click `Authorize`.
3. Enter:
   - `username` = your account email
   - `password` = your account password
4. Submit (uses `POST /api/v1/auth/token`).

### Option B
1. Call `POST /api/v1/auth/login` with JSON.
2. Copy `access_token`.
3. Click `Authorize` and paste `Bearer <token>`.

## Notes

- Dataset name must be unique per organization.
- Email is globally unique.
- Password hashing uses passlib+bcrypt; bcrypt passwords must be <= 72 bytes.

## Git Push Checklist

```powershell
git status
git add .
git commit -m "phase2: dataset upload and metadata foundation"
git push
```

Ensure `.env` is not committed.
