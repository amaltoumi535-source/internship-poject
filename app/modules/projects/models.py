# app/modules/projects/models.py
"""ORM model for projects."""

from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime

from app.modules.storage.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String, nullable=True, default="from-blue-500 to-purple-600")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)