# app/db.py
"""
Shared FastAPI dependency for database sessions.
Provides get_db(), a generator that yields a SQLAlchemy Session and
guarantees it's closed after the request, for use with Depends(get_db).
"""

from app.modules.storage.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()