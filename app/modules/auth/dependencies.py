"""Shared auth dependency for verifying JWT tokens across modules."""

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify JWT token and return the user_id (sub claim)."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            os.getenv("SECRET_KEY", "your-secret-key-change-in-prod"),
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.InvalidTokenError as e:
        logger.error(f"Token validation failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")