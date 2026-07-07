healthcare-claims-api/
│
├── app/
│   ├── __init__.py
│   ├── main.py              ← FastAPI app starts here
│   ├── models/
│   │   ├── __init__.py
│   │   └── claim.py         ← Pydantic + DB models
│   ├── routes/
│   │   ├── __init__.py
│   │   └── claims.py        ← POST /claims/upload endpoint
│   ├── auth/
│   │   ├── __init__.py
│   │   └── jwt_handler.py   ← JWT logic
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py      ← PostgreSQL connection
│   └── audit/
│       ├── __init__.py
│       └── logger.py        ← HIPAA audit log
│
├── .env                     ← secrets (DB URL, JWT secret)
├── requirements.txt
└── README.md

to generate a hash:
python -c "import bcrypt; print(bcrypt.hashpw(b'secret', bcrypt.gensalt()).decode())"

for run the app
uvicorn app.main:app --reload