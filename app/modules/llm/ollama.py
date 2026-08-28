"""Ollama client helpers (HTTP) for local Ollama server.

Provides:
- generate(prompt, model, max_tokens, temperature)
- summarize(text, prompt_template, model, ...)
- summarize_chunk(text, prompt_template, model, ...)
- answer(context, question, model, ...)
"""

from typing import Optional
import os
import logging
import requests

from app.config import get_settings
from app.modules.analysis.prompts import SINGLE_DOC_SUMMARY, CHUNK_SUMMARY

logger = logging.getLogger(__name__)
settings = get_settings()


def _build_prompt(prompt_template: str, document_text: str) -> str:
    prompt = prompt_template.format(document_text=document_text, chunk_text=document_text)
    if not prompt.endswith("\n"):
        prompt = prompt + "\n"
    return prompt


def _ollama_post(url: str, payload: dict, timeout: int = 60) -> dict:
    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        logger.exception("Ollama request failed: %s", exc)
        raise RuntimeError(f"Ollama request failed: {exc}") from exc


def _parse_ollama_response(j: dict) -> str:
    """
    Extract generated text from common Ollama response shapes.
    """
    for key in ("completion", "response", "text", "result", "output"):
        if key in j and isinstance(j[key], str):
            return j[key].strip()

    results = j.get("results") or j.get("outputs") or j.get("choices")
    if isinstance(results, list) and results:
        first = results[0]
        if isinstance(first, dict):
            content = first.get("content") or first.get("message") or first.get("output")
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("text"):
                        return item.get("text").strip()
            for v in first.values():
                if isinstance(v, str) and v.strip():
                    return v.strip()

    try:
        import json
        return json.dumps(j)
    except Exception:
        return str(j)


def _resolve_generate_url() -> str:
    base = os.environ.get("OLLAMA_URL") or getattr(settings, "OLLAMA_URL", None) or "http://localhost:11434"
    base = base.rstrip("/")
    # prefer /api/generate
    return f"{base}/api/generate"


def generate(prompt: str, model: Optional[str] = None, max_tokens: int = 300, temperature: float = 0.0, timeout: int = 60) -> str:
    """
    Send a generation request to the local Ollama server.
    """
    model_name = model or getattr(settings, "OLLAMA_MODEL", None) or "llama"
    url = _resolve_generate_url()
    payload = {
        "model": model_name,
        "prompt": prompt,
        "maxTokens": max_tokens,
        "temperature": temperature,
    }

    j = _ollama_post(url, payload, timeout=timeout)
    return _parse_ollama_response(j)


def summarize(text: str, prompt_template: str = SINGLE_DOC_SUMMARY, model: Optional[str] = None, max_tokens: int = 256, temperature: float = 0.0) -> str:
    prompt = _build_prompt(prompt_template, text)
    return generate(prompt, model=model, max_tokens=max_tokens, temperature=temperature)


def summarize_chunk(text: str, prompt_template: str = CHUNK_SUMMARY, model: Optional[str] = None, max_tokens: int = 128, temperature: float = 0.0) -> str:
    prompt = _build_prompt(prompt_template, text)
    return generate(prompt, model=model, max_tokens=max_tokens, temperature=temperature)


def answer(context: str, question: str, model: Optional[str] = None, max_tokens: int = 256, temperature: float = 0.0) -> str:
    prompt = (
        "You are an assistant that uses the provided context to answer the question.\n\n"
        "Context:\n"
        f"{context}\n\n"
        "Question:\n"
        f"{question}\n\n"
        "Answer concisely and cite relevant facts from the context when possible.\n\nAnswer:"
    )
    return generate(prompt, model=model, max_tokens=max_tokens, temperature=temperature)