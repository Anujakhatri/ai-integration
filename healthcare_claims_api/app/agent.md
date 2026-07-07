# 🏥 Healthcare Claims API — Project Notes

## Step 1: Project Architecture — Bird's Eye View

```
CSV File Upload
    ↓
FastAPI (POST /claims/upload)
    ↓
JWT Authentication check → RBAC check (admin only)
    ↓
Pydantic validation (per row)
    ↓
PostgreSQL (claims table + audit_log table)
    ↓
Response: {uploaded_by, total_records, valid, invalid, errors}
```

### Project Structure

```
healthcare-claims-api/
│
├── app/
│   ├── __init__.py
│   ├── main.py              ← FastAPI app starts here
│   ├── models/
│   │   ├── __init__.py
│   │   └── claim.py         ← SQLAlchemy DB model + Pydantic schema
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py          ← POST /auth/login
│   │   └── claims.py        ← POST /claims/upload, GET /claims/
│   ├── auth/
│   │   ├── __init__.py
│   │   └── jwt_handler.py   ← JWT logic + RBAC dependencies
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py      ← PostgreSQL connection
│   └── audit/
│       ├── __init__.py
│       └── logger.py        ← Strict audit log writer
│
├── .env                     ← secrets (never push to GitHub!)
├── .env.example             ← template (safe to push)
├── .dockerignore
├── docker-compose.yml
├── Dockerfile
├── mypy.ini
├── requirements.txt
└── README.md
```

### Why This Structure?

| Folder | Responsibility | Principle |
|--------|---------------|-----------|
| `models/` | Data shape define garchha | Single Responsibility |
| `routes/` | HTTP endpoints matra | Separation of Concerns |
| `auth/` | JWT logic alag | Modularity |
| `db/` | DB connection alag | Don't Repeat Yourself |
| `audit/` | Logging alag | Open/Closed Principle |

---

## Step 2: Database Connection

- `DATABASE_URL` `.env` bata load garchha
- SQLAlchemy `engine` = Django ko `settings.py` DATABASES jastai
- `SessionLocal` = har request ko lagi ek DB session
- `Base` = sabai models inherit garchhan (Django ko `models.Model` jastai)
- `get_db()` = FastAPI dependency — request sakepaxi session auto-close huncha (`yield` use gareko)

### Django vs FastAPI DB

| Concept | Django | FastAPI (SQLAlchemy) |
|---------|--------|----------------------|
| DB config | `settings.py` | `database.py` + `.env` |
| Models inherit | `models.Model` | `Base` |
| DB session | automatic | `get_db()` manually inject |
| Migrations | `manage.py migrate` | Alembic (manual) |

---

## Step 3: Claim Model + Pydantic Validation

**Key insight:** Django ma model + validation alag alag huncha (serializer chaiyo). FastAPI ma:
- `Claim` (SQLAlchemy) = DB table
- `ClaimSchema` (Pydantic) = input validation — serializer nai chaidaina!

### ICD-10 Regex — `^[A-Z]\d{2}\.?\d{0,4}$`

```
^        = string suru
[A-Z]    = ek uppercase letter  → J
\d{2}    = exactly 2 digits     → 18
\.?      = dot optional         → .
\d{0,4}  = 0 to 4 digits       → 9
$        = string end

J18.9    ✅
A01      ✅
B02.1234 ✅
XYZ999   ❌
j18.9    ❌ (lowercase reject)
```

### Create PostgreSQL Database + Table

```bash
# Create database in postgresql
psql -U postgres
CREATE DATABASE claims_db;
\q

# create a table on python
python -c "
from app.db.database import engine, Base
from app.models.claim import Claim
Base.metadata.create_all(bind=engine)
print('Table created!')
"
```

---

## Step 4: JWT Auth — How It Works

```
User login garchha (username + password)
    ↓
Server verify garchha → Token banaucha
    ↓
Token = "eyJhbGc..." (encrypted string)
    ↓
User le har request ma yo token pathaucha
    ↓
Server le token decode garchha → "Oh, yo admin ho!"
```

**Django ma** — `rest_framework_simplejwt` le sab automatic gardinthyo.
**FastAPI ma** — hami afai banauchu, so internals thaha huncha!

### Install

```bash
pip install "python-jose[cryptography]" bcrypt
```

- `python-jose` = JWT encode/decode
- `bcrypt` = password hashing

### JWT Secret Key Generate Gara

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

### JWT Payload — Token Bhitra K Huncha?

```python
{
    "sub": "admin_user",   # subject = username
    "role": "admin",       # RBAC ko lagi
    "exp": 1718123456      # expire time (30 min)
}
```

### `jwt_handler.py` — Complete Code

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os
import bcrypt as bcrypt_lib

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET", "fallback-secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_fake_users():
    return {
        "admin_user": {
            "username": "admin_user",
            "hashed_password": os.getenv("ADMIN_HASHED_PASSWORD"),
            "role": "admin",
        },
        "read_only_user": {
            "username": "read_only_user",
            "hashed_password": os.getenv("READONLY_HASHED_PASSWORD"),
            "role": "read_only"
        }
    }

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_lib.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )

def get_password_hash(password: str) -> str:
    salt = bcrypt_lib.gensalt()
    return bcrypt_lib.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")   # "sub" key — create_access_token sanga match!
        role: str = payload.get("role")
        if username is None:
            raise credentials_exception
        return {"username": username, "role": role}
    except JWTError:
        raise credentials_exception

def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to access this resource"
        )
    return current_user
```

### Hashed Password — .env bata load gara (never hardcode!)

```bash
# To generate hash
python -c "import bcrypt; print(bcrypt.hashpw(b'yourpassword', bcrypt.gensalt()).decode())"

# put in .env file
ADMIN_HASHED_PASSWORD=$2b$12$xxxxx...
READONLY_HASHED_PASSWORD=$2b$12$xxxxx...
```

### RBAC — Role Based Access Control

```
admin_user     → ✅ POST /claims/upload
               → ✅ GET /claims/
               → ✅ GET /claims/audit-logs

read_only_user → ❌ POST /claims/upload  (403 Forbidden)
               → ✅ GET /claims/
               → ❌ GET /claims/audit-logs (403 Forbidden)
```

**Unauthorized (401)** = if user don't have token.
**Forbidden (403)** = token exist but permission not allowed.

---

## Step 5: CSV Upload Endpoint

- Admin only — `require_admin` dependency use gareko
- CSV row by row validate garchha — Pydantic `ClaimSchema` use garcha
- Valid rows PostgreSQL ma store garchha
- Invalid rows `errors` list ma collect garchha
- Ek palta `db.commit()` — sabai valid rows sanga

### CSV Format

```csv
member_id,icd10_code,cpt_code,paid_amount,date_of_service
MEM001,J18.9,99213,15000.00,2024-01-15
MEM002,A01.0,99214,8500.50,2024-02-20
MEM003,INVALID,99215,5000.00,2024-03-10   ← invalid ICD-10 ❌
MEM004,B02.1,99212,12000.00,2027-01-01   ← future date ❌
```

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
      "data": {"icd10_code": "INVALID", "...": "..."},
      "error": "Invalid ICD-10 code: INVALID"
    }
  ]
}
```

### Important Fix — date string → date object

```python
#mypy error!!
# CSV bata date string aaucha so convert garnu parchha
from datetime import date

date_of_service=date.fromisoformat(row["date_of_service"])  # "2024-01-15" → date object
```

---

## Step 6: strict Audit Log

strict rule: "Patient data access/upload ko complete record hunuparchha"

Every upload automatically log huncha:

| Field | Description |
|-------|-------------|
| `username` | Ko le upload garo |
| `action` | `CSV_UPLOAD` |
| `filename` | Kun file upload bho |
| `total` | Kati records thiye |
| `valid` | Kati store bhayo |
| `invalid` | Kati reject bhayo |
| `timestamp` | Kati baje bho |

---

## Step 7: Docker + GitHub Actions

### Docker Commands

```bash
# Build + start
docker-compose up --build

# Stop
docker-compose down

# Logs hera
docker-compose logs api
```

### GitHub Secrets — Sensitive Values

GitHub repository → Settings → Secrets and variables → Actions:

```
ADMIN_HASHED_PASSWORD    = <bcrypt hash>
READONLY_HASHED_PASSWORD = <bcrypt hash>
```

CI/CD ma `${{ secrets.ADMIN_HASHED_PASSWORD }}` use garchha — never expose hunna!

---

## Common Bugs Encountered + Fixes

| Bug | Cause | Fix |
|-----|-------|-----|
| `ModuleNotFoundError: app.claims` | Wrong import path | `app.models.claim` use gara |
| `ValueError: Invalid salt` | Fake hash string used | Real bcrypt hash generate gara |
| `AttributeError: NoneType encode` | `.env` key name mismatch | Key names exactly match gara |
| `401 Unauthorized` on Swagger | Authorize button click nagari | `/docs` ma Authorize → login gara |
| `payload.get("username")` = None | Wrong JWT key | `"sub"` key use gara |
| `zsh: no matches found` | `[]` zsh special char | Quotes ma wrap gara: `"bcrypt[...]"` |
| `fromisoformate` typo | Typo | `fromisoformat` (no trailing e) |

---

## mypy Setup

```ini
# mypy.ini
[mypy]
ignore_missing_imports = True
```

```bash
mypy .   # 0 errors aaunuparchha
```

---

## Final Checklist

```
✅ Project structure
✅ PostgreSQL connection (SQLAlchemy)
✅ Claim model + ICD-10 + date validation (Pydantic)
✅ JWT auth + bcrypt password hashing
✅ RBAC (admin / read_only)
✅ CSV upload endpoint
✅ Strict audit log
✅ Docker + docker-compose
✅ GitHub Actions CI/CD
✅ mypy type checking
✅ README.md
```