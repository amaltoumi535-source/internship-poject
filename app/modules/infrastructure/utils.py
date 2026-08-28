"""Small utility helpers used across the app."""

import os
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional


def generate_id(prefix: Optional[str] = None) -> str:
    """Return a stable unique id string (uuid4)."""
    uid = str(uuid.uuid4())
    return f"{prefix}-{uid}" if prefix else uid


def timestamp_now() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def ensure_dir(path: str) -> None:
    """Ensure a directory exists (recursive)."""
    os.makedirs(path, exist_ok=True)


def safe_json_dumps(obj: Any, **kwargs) -> str:
    """Dump JSON with defaults that handle non-serializable objects gracefully."""
    def _default(o):
        try:
            return o.__dict__
        except Exception:
            return str(o)
    return json.dumps(obj, default=_default, ensure_ascii=False, indent=2, **kwargs)


def chunk_preview(text: str, length: int = 200) -> str:
    """Return a short preview for a long text (single-line)."""
    if not text:
        return ""
    s = " ".join(text.split())
    if len(s) <= length:
        return s
    return s[:length].rstrip() + "…"