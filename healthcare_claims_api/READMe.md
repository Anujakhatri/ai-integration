# 🏥 Healthcare Claims Ingestion API

A Strict-aware REST API for ingesting, validating, and managing healthcare insurance claims — built with FastAPI, PostgreSQL, JWT authentication, and Role-Based Access Control (RBAC).

---

## 📋 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Setup](#local-setup)
  - [Docker Setup](#docker-setup)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Authentication & RBAC](#authentication--rbac)
- [CSV Format](#csv-format)
- [Strict Audit Log](#Strict-audit-log)
- [Running Tests](#running-tests)
- [CI/CD](#cicd)

---

## Overview

This API simulates a real-world healthcare claims ingestion system where hospitals submit insurance claims in bulk via CSV. It validates each claim against healthcare standards (ICD-10 codes, CPT codes, date rules), stores valid records in PostgreSQL, and maintains a full Strict-compliant audit trail.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| Database | PostgreSQL + SQLAlchemy ORM |
| Validation | Pydantic v2 |
| Authentication | JWT (python-jose) |
| Password Hashing | bcrypt |
| Containerization | Docker + Docker Compose |
| CI/CD | GitHub Actions |

---

## Project Structure

```
healthcare-claims-api/
├── .github/
│   └── workflows/
│       └── ci.yml              ← GitHub Actions CI pipeline
├── app/
│   ├── main.py                 ← FastAPI app entry point
│   ├── models/
│   │   └── claim.py            ← SQLAlchemy models + Pydantic schemas
│   ├── routes/
│   │   ├── auth.py             ← Login endpoint
│   │   └── claims.py           ← Claims upload + query endpoints
│   ├── auth/
│   │   └── jwt_handler.py      ← JWT logic + RBAC dependencies
│   ├── db/
│   │   └── database.py         ← PostgreSQL connection + session
│   └── audit/
│       └── logger.py           ← Strict audit log writer
├── .env.example                ← Environment variable template
├── .dockerignore
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Features

- **CSV Bulk Upload** — Upload thousands of claims in one request
- **ICD-10 Validation** — Regex-based format validation (`J18.9`, `A01`, `B02.1234`)
- **Date Validation** — Rejects future dates of service
- **JWT Authentication** — Secure token-based auth (30-minute expiry)
- **RBAC** — Admin vs Read-Only role enforcement
- **Strict Audit Log** — Tracks who uploaded what, when, and how many records
- **Upload Summary** — Returns `{total, valid, invalid, errors}` per upload
- **Swagger UI** — Interactive API docs at `/docs`

---

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL 15+
- Docker & Docker Compose (optional)

---

### Local Setup

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/healthcare-claims-api.git
cd healthcare-claims-api
```

**2. Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your actual values
```

**5. Create PostgreSQL database**
```bash
psql -U postgres
CREATE DATABASE claims_db;
\q
```

**6. Run the server**
```bash
uvicorn app.main:app --reload
```

**7. Open Swagger UI**
```
http://localhost:8000/docs
```

---

### Docker Setup

**1. Build and start all services**
```bash
docker-compose up --build
```

**2. Open Swagger UI**
```
http://localhost:8000/docs
```

**Stop services**
```bash
docker-compose down
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/claims_db` |
| `JWT_SECRET` | Secret key for JWT signing | `your-secret-key` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ADMIN_HASHED_PASSWORD` | Bcrypt hash of admin password | `$2b$12$...` |
| `READONLY_HASHED_PASSWORD` | Bcrypt hash of read-only password | `$2b$12$...` |

**Generate bcrypt password hash:**
```bash
python -c "import bcrypt; print(bcrypt.hashpw(b'yourpassword', bcrypt.gensalt()).decode())"
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `POST` | `/auth/login` | Login and get JWT token | Public |

### Claims

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `POST` | `/claims/upload` | Upload CSV file of claims | Admin only |
| `GET` | `/claims/` | List all claims | Admin + Read-Only |
| `GET` | `/claims/audit-logs` | View Strict audit logs | Admin only |

---

## Authentication & RBAC

This API uses **JWT Bearer token** authentication with two roles:

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin_user&password=yourpassword"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "role": "admin"
}
```

### Role Permissions

| Endpoint | admin | read_only |
|----------|-------|-----------|
| `POST /claims/upload` | ✅ | ❌ 403 |
| `GET /claims/` | ✅ | ✅ |
| `GET /claims/audit-logs` | ✅ | ❌ 403 |

---

## CSV Format

Upload claims using this CSV format:

```csv
member_id,icd10_code,cpt_code,paid_amount,date_of_service
MEM001,J18.9,99213,15000.00,2024-01-15
MEM002,A01.0,99214,8500.50,2024-02-20
```

### Field Rules

| Field | Format | Example | Rule |
|-------|--------|---------|------|
| `member_id` | String | `MEM001` | Required |
| `icd10_code` | `[A-Z]\d{2}\.?\d{0,4}` | `J18.9` | Must match ICD-10 format |
| `cpt_code` | String | `99213` | Required |
| `paid_amount` | Float | `15000.00` | Required |
| `date_of_service` | `YYYY-MM-DD` | `2024-01-15` | Cannot be future date |

### Upload Response

```json
{
  "uploaded_by": "admin_user",
  "total_records": 4,
  "valid": 2,
  "invalid": 2,
  "errors": [
    {
      "row": 4,
      "data": { "icd10_code": "INVALID", "..." : "..." },
      "error": "Invalid ICD-10 code: INVALID"
    }
  ]
}
```

---

## Strict Audit Log

Every upload is automatically logged with:

| Field | Description |
|-------|-------------|
| `username` | Who uploaded |
| `action` | `CSV_UPLOAD` or `QUERY` |
| `filename` | Which file was uploaded |
| `total` | Total records in file |
| `valid` | Successfully stored records |
| `invalid` | Rejected records |
| `timestamp` | Exact date and time |

**View audit logs:**
```bash
curl http://localhost:8000/claims/audit-logs \
  -H "Authorization: Bearer <your_token>"
```

---

## Running Tests(if you want to test with each case)

```bash
pytest app/tests/ -v
```

---

## CI/CD

GitHub Actions pipeline runs on every push to `main`:

1. **Test job** — Spins up PostgreSQL, runs pytest
2. **Docker job** — Builds Docker image (runs only after tests pass)

Pipeline file: `.github/workflows/ci.yml`

---

## Author

**Anuja Khatri**
FastAPI | Django | PostgreSQL
[GitHub](https://github.com/anujakhatri) • [LinkedIn](https://linkedin.com/in/anujakhatri)
