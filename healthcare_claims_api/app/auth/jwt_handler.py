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

# FastAPI le Authorization header bata token lanchha
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

#for trial
FAKE_USERS ={
    "admin_user":{
        "username":"admin_user",
        "hashed_password":os.getenv("ADMIN_HASHED_PASSWORD"),
        "role":"admin",
    },
    "read_only_user":{
        "username":"read_only_user",
        "hashed_password" : os.getenv("READONLY_HASHED_PASSWORD"),
        "role" : "read_only"
    }
}

#helper functions:

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_lib.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"))

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
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise credentials_exception
        return {"username": username, "role": role}
    except JWTError:
        raise credentials_exception

def require_admin(current_user: dict=Depends(get_current_user)) -> dict:
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = "You are not allowed to access this resource"
        )
    return current_user