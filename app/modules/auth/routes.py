"""Authentication routes: signup, verify, signin."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
import os
import logging
import bcrypt

from app.db import get_db
from app.modules.auth.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


class SignUpRequest(BaseModel):
    email: str
    password: str
    fullName: str


class SignInRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str


def hash_password(password: str) -> str:
    """Hash password using bcrypt with 72 byte limit."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password[:72].encode('utf-8'), salt).decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    """Verify password using bcrypt with 72 byte limit."""
    try:
        return bcrypt.checkpw(plain[:72].encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False


def create_access_token(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=30)
    }
    token = jwt.encode(
        payload,
        os.getenv("SECRET_KEY", "your-secret-key-change-in-prod"),
        algorithm="HS256"
    )
    return token


@router.post("/signup")
async def signup(req: SignUpRequest, db: Session = Depends(get_db)):
    """Sign up new user - auto verified."""
    
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        full_name=req.fullName,
        is_verified=True
    )
    db.add(user)
    db.commit()
    
    logger.info(f"User created: {req.email}")
    return {"message": "Account created successfully", "email": req.email}


@router.post("/signin", response_model=TokenResponse)
async def signin(req: SignInRequest, db: Session = Depends(get_db)):
    """Sign in user and return JWT token."""
    
    user = db.query(User).filter(User.email == req.email).first()
    
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")
    
    token = create_access_token(user.id, user.email)
    
    logger.info(f"User signed in: {user.email}")
    return TokenResponse(access_token=token, user_id=user.id)