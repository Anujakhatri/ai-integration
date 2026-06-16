from fastapi import FastAPI
from app.db.database import engine, Base
from app.models.claim import Claim
from app.routes.auth import router as auth_router

Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="Healthcare Claims API",
    description="Healthcare Claims investigation API",
    version="1.0.0",
)

app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "Welcome to Healthcare Claims API running!"}