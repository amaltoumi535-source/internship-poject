"""Messages API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt
import os

from app.db import get_db
from app.modules.auth.models import User
from app.modules.auth.models import Message # type: ignore

router = APIRouter(prefix="/api/messages", tags=["messages"])
security = HTTPBearer()


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            os.getenv("SECRET_KEY", "your-secret-key-change-in-prod"),
            algorithms=["HS256"]
        )
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/history")
async def get_message_history(token: dict = Depends(verify_token), db: Session = Depends(get_db)):
    """Get user's message history."""
    user_id = token.get("sub")
    
    messages = db.query(Message).filter(Message.user_id == user_id).order_by(Message.created_at).all()
    
    return {
        "messages": [
            {
                "id": m.id,
                "type": m.message_type,
                "content": m.content,
                "timestamp": m.created_at.isoformat()
            }
            for m in messages
        ]
    }