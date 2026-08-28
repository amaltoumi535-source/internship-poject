"""Chat management endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
import jwt 
import os

from app.db import get_db
from app.modules.auth.models import User, Chat, Message

router = APIRouter(prefix="/api/chats", tags=["chats"])
security = HTTPBearer()


class UpdateTitleRequest(BaseModel):
    title: str


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


@router.post("/new")
async def create_new_chat(token: dict = Depends(verify_token), db: Session = Depends(get_db)):
    """Create a new chat."""
    user_id = token.get("sub")
    
    chat = Chat(user_id=user_id, title="New Chat")
    db.add(chat)
    db.commit()
    db.refresh(chat)
    
    return {"chat_id": chat.id, "title": chat.title}


@router.get("/list")
async def list_chats(token: dict = Depends(verify_token), db: Session = Depends(get_db)):
    """List all chats for user."""
    user_id = token.get("sub")
    
    chats = db.query(Chat).filter(Chat.user_id == user_id).order_by(Chat.created_at.desc()).all()
    
    return {
        "chats": [
            {"id": c.id, "title": c.title, "created_at": c.created_at.isoformat()}
            for c in chats
        ]
    }


@router.get("/{chat_id}/messages")
async def get_chat_messages(chat_id: int, token: dict = Depends(verify_token), db: Session = Depends(get_db)):
    """Get messages for a specific chat."""
    user_id = token.get("sub")
    
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    messages = db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at).all()
    
    return {
        "chat_id": chat_id,
        "title": chat.title,
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


@router.put("/{chat_id}/title")
async def update_chat_title(
    chat_id: int, 
    request: UpdateTitleRequest,
    token: dict = Depends(verify_token), 
    db: Session = Depends(get_db)
):
    """Update chat title."""
    user_id = token.get("sub")
    
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    chat.title = request.title
    db.commit()
    
    return {"chat_id": chat_id, "title": chat.title}


@router.delete("/{chat_id}")
async def delete_chat(chat_id: int, token: dict = Depends(verify_token), db: Session = Depends(get_db)):
    """Delete a chat and its messages."""
    user_id = token.get("sub")
    
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    db.query(Message).filter(Message.chat_id == chat_id).delete()
    db.delete(chat)
    db.commit()
    
    return {"deleted": True}