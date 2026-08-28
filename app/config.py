# app/config.py
"""
Application configuration using pydantic-settings (compatible with Pydantic v2).

Fields use snake_case attribute names. pydantic-settings automatically matches
environment variables to field names case-insensitively (e.g. LOG_LEVEL,
Log_Level, log_level all bind to `log_level`), so no explicit `env=` aliasing
is needed. model_config sets extra="allow" so environment parsing differences
don't raise extra_forbidden errors.
"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Environment
    env: str = "development"
    debug: bool = True
    log_level: str = "info"

    # App server
    host: str = "127.0.0.1"
    port: int = 8000

    # Auth
    secret_key: str = "amal-itgate-super-secret-key-change-in-prod"
    
    # Local paths and tools
    data_dir: str = "data"
    files_dir: Optional[str] = None
    poppler_path: Optional[str] = None
    tessdata_prefix: Optional[str] = None

    # Vectorization / embeddings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chromadb_dir: str = "data/chromadb"
    enable_vector_store: bool = False

    # LLM provider and models
    llm_provider: str = "anthropic"
    anthropic_model: str = "claude-sonnet"

    # Ollama settings (local server)
    ollama_url: Optional[str] = "http://localhost:11434"
    ollama_model: Optional[str] = None

    # Tell pydantic-settings to read the .env file and allow extra env inputs
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        # allow extra so differing env name normalizations won't break init
        "extra": "allow",
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()