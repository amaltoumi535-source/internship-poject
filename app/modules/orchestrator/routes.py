from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from langchain_core.messages import HumanMessage, AIMessage
from sqlalchemy.orm import Session
from pydantic import BaseModel
import jwt
import os
import logging

from app.modules.orchestrator.agent import orchestrator
from app.db import get_db
from app.modules.auth.models import User, Chat, Message
from app.modules.search.agent import current_user_id as search_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["orchestrator"])
security = HTTPBearer()

MAX_HISTORY_MESSAGES = 12  # cap to control token usage; most recent N messages


class ChatRequest(BaseModel):
    message: str
    chat_id: int


class ChatResponse(BaseModel):
    response: str


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token from Authorization header."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            os.getenv("SECRET_KEY", "your-secret-key-change-in-prod"),
            algorithms=["HS256"]
        )
        return payload
    except jwt.InvalidTokenError as e:
        logger.error(f"Token validation failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")


def _load_history(db: Session, chat_id: int, limit: int = MAX_HISTORY_MESSAGES):
    """Load recent prior messages for this chat, oldest first, as LangChain messages."""
    rows = (
        db.query(Message)
        .filter(Message.chat_id == chat_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
        .all()
    )
    rows.reverse()  # oldest first

    history = []
    for row in rows:
        if row.message_type == "user":
            history.append(HumanMessage(content=row.content))
        elif row.message_type == "assistant":
            history.append(AIMessage(content=row.content))
    return history


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, token: dict = Depends(verify_token), db: Session = Depends(get_db)):
    """Chat endpoint - requires valid JWT token, saves messages to database."""

    user_id = token.get("sub")
    chat_id = request.chat_id

    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Verify chat belongs to user
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    try:
        # Load prior conversation BEFORE saving the new user message,
        # so the new message isn't duplicated in history.
        history = _load_history(db, chat_id)

        # Save user message
        user_msg = Message(user_id=user_id, chat_id=chat_id, content=request.message, message_type="user")
        db.add(user_msg)
        db.commit()

        logger.info(f"Chat request from user {user.email}: {request.message[:50]}...")

        # Get response from orchestrator, with full recent history + new message
        messages = history + [HumanMessage(content=request.message)]

        # Make the requesting user's id visible to search tools for this
        # request only, so semantic/literal search is scoped to their own
        # documents. ctx_token (not to be confused with the JWT `token` param
        # above) is used to reset the context var afterward.
        ctx_token = search_current_user_id.set(user_id)
        try:
            result = await orchestrator.ainvoke({"messages": messages})
            assistant_response = result["messages"][-1].content
        except Exception as agent_err:
            logger.exception("Orchestrator invocation failed")
            assistant_response = (
                "I ran into a technical issue while processing that request. "
                "Could you try rephrasing your question?"
            )
        finally:
            search_current_user_id.reset(ctx_token)

        # Save assistant response
        assistant_msg = Message(user_id=user_id, chat_id=chat_id, content=assistant_response, message_type="assistant")
        db.add(assistant_msg)
        db.commit()

        # Auto-title: if first message, generate title from it
        msg_count = db.query(Message).filter(Message.chat_id == chat_id).count()
        if msg_count == 2:  # Just user + assistant
            title = request.message[:50]
            chat.title = title
            db.commit()

        logger.info(f"Response saved for user {user.email}")

        return ChatResponse(response=assistant_response)

    except Exception as e:
        logger.exception("Chat error")
        raise HTTPException(status_code=500, detail=str(e))