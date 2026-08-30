"""Authentication routes: signup, verify, signin."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from urllib.parse import quote
import jwt
import os
import logging
import bcrypt

from app.db import get_db
from app.modules.auth.models import User, VerificationCode
from app.modules.auth.email_service import email_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


class SignUpRequest(BaseModel):
    email: str
    password: str
    fullName: str


class VerifyEmailRequest(BaseModel):
    email: str
    code: str


class SignInRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    email: str
    code: str
    new_password: str


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
    """Sign up new user - unverified until email link is confirmed.
    If an unverified account already exists for this email, refresh it
    and resend the verification link instead of blocking."""

    existing = db.query(User).filter(User.email == req.email).first()

    if existing and existing.is_verified:
        raise HTTPException(status_code=400, detail="Email already registered")

    if existing and not existing.is_verified:
        # Unverified account already exists — update it and resend the link,
        # rather than leaving the user permanently stuck.
        existing.hashed_password = hash_password(req.password)
        existing.full_name = req.fullName
        db.commit()
        user = existing
    else:
        user = User(
            email=req.email,
            hashed_password=hash_password(req.password),
            full_name=req.fullName,
            is_verified=False
        )
        db.add(user)
        db.commit()

    code = email_service.generate_code()
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    existing_code = db.query(VerificationCode).filter(VerificationCode.email == req.email).first()
    if existing_code:
        existing_code.code = code
        existing_code.expires_at = expires_at
        existing_code.attempts = 0
    else:
        existing_code = VerificationCode(email=req.email, code=code, expires_at=expires_at, attempts=0)
        db.add(existing_code)
    db.commit()

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    verify_url = f"{frontend_url}/auth/verify-email?email={quote(req.email)}&code={code}"

    sent = email_service.send_verification_email(req.email, verify_url)
    if not sent:
        logger.error(f"Failed to send verification email to {req.email}")

    logger.info(f"User created/updated (unverified): {req.email}")
    return {"message": "Account created. Please check your email to verify.", "email": req.email}


@router.post("/verify-email", response_model=TokenResponse)
async def verify_email(req: VerifyEmailRequest, db: Session = Depends(get_db)):
    """Verify the signup code (from the emailed link) and activate the account,
    returning a session token."""

    record = db.query(VerificationCode).filter(VerificationCode.email == req.email).first()

    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired verification link")

    if record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Verification link has expired")

    if record.attempts >= 5:
        raise HTTPException(status_code=429, detail="Too many attempts. Please request a new link.")

    if record.code != req.code:
        record.attempts += 1
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid verification link")

    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification link")

    user.is_verified = True
    db.delete(record)
    db.commit()

    token = create_access_token(user.id, user.email)

    logger.info(f"User verified: {user.email}")
    return TokenResponse(access_token=token, user_id=user.id)


@router.post("/resend-verification")
async def resend_verification(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Resend a new signup verification link."""

    user = db.query(User).filter(User.email == req.email).first()
    if user and not user.is_verified:
        code = email_service.generate_code()
        expires_at = datetime.utcnow() + timedelta(minutes=10)

        existing_code = db.query(VerificationCode).filter(VerificationCode.email == req.email).first()
        if existing_code:
            existing_code.code = code
            existing_code.expires_at = expires_at
            existing_code.attempts = 0
        else:
            existing_code = VerificationCode(email=req.email, code=code, expires_at=expires_at, attempts=0)
            db.add(existing_code)
        db.commit()

        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        verify_url = f"{frontend_url}/auth/verify-email?email={quote(req.email)}&code={code}"
        email_service.send_verification_email(req.email, verify_url)

    return {"message": "If that email needs verification, a new link has been sent."}


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


@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Generate a reset code and email it, if the account exists.
    Always returns success to avoid leaking whether an email is registered."""

    user = db.query(User).filter(User.email == req.email).first()

    if user:
        code = email_service.generate_code()
        expires_at = datetime.utcnow() + timedelta(minutes=10)

        existing_code = db.query(VerificationCode).filter(VerificationCode.email == req.email).first()
        if existing_code:
            existing_code.code = code
            existing_code.expires_at = expires_at
            existing_code.attempts = 0
        else:
            existing_code = VerificationCode(
                email=req.email,
                code=code,
                expires_at=expires_at,
                attempts=0,
            )
            db.add(existing_code)
        db.commit()

        sent = email_service.send_password_reset_email(req.email, code)
        if not sent:
            logger.error(f"Failed to send password reset email to {req.email}")

    return {"message": "If that email is registered, a reset code has been sent."}


@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Verify the reset code and set a new password."""

    record = db.query(VerificationCode).filter(VerificationCode.email == req.email).first()

    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired code")

    if record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Code has expired")

    if record.attempts >= 5:
        raise HTTPException(status_code=429, detail="Too many attempts. Please request a new code.")

    if record.code != req.code:
        record.attempts += 1
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid code")

    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired code")

    if len(req.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if len(req.new_password) > 72:
        raise HTTPException(status_code=400, detail="Password must not exceed 72 characters")

    user.hashed_password = hash_password(req.new_password)
    db.delete(record)
    db.commit()

    logger.info(f"Password reset for user: {req.email}")
    return {"message": "Password reset successfully"}