# app/modules/projects/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = None


class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    doc_count: int = 0
    chat_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True