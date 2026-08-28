"""SQLAlchemy engine, sessionmaker and declarative Base for storage."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import get_settings
from app.modules.infrastructure.utils import ensure_dir

settings = get_settings()

# Use configured DATA_DIR (fallback to "data")
DATA_DIR = settings.data_dir or "data"
DB_DIR = os.path.join(os.getcwd(), DATA_DIR)
ensure_dir(DB_DIR)

SQLITE_PATH = os.path.join(DB_DIR, "storage.db")
DATABASE_URL = f"sqlite:///{SQLITE_PATH}"

# SQLite: check_same_thread=False for multi-threaded frameworks (uvicorn)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass