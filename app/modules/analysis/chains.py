"""
Top-level chains helpers that dispatch to the configured LLM provider.
Supports 'ollama', 'anthropic', 'openai' (if those helpers are present).
"""

from typing import Optional
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _get_ollama():
    try:
        from app.modules.llm import ollama as _ollama_mod  # type: ignore
        return _ollama_mod
    except Exception as exc:
        logger.debug("Ollama module not available: %s", exc)
        raise RuntimeError("Ollama module not available") from exc


def _provider() -> str:
    return (getattr(settings, "LLM_PROVIDER", None) or "none").lower()


def summarize_with_llm(text: str, prompt_template: Optional[str] = None, model: Optional[str] = None, max_tokens: int = 256, temperature: float = 0.0) -> str:
    provider = _provider()
    if provider == "ollama":
        ollama = _get_ollama()
        prompt = prompt_template or None
        if prompt:
            return ollama.summarize(text, prompt_template=prompt, model=model, max_tokens=max_tokens, temperature=temperature)
        return ollama.generate(text, model=model, max_tokens=max_tokens, temperature=temperature)

    raise RuntimeError(f"No supported LLM provider configured (LLM_PROVIDER={provider})")


def answer_with_llm(context: str, question: str, model: Optional[str] = None, max_tokens: int = 256, temperature: float = 0.0) -> str:
    provider = _provider()
    if provider == "ollama":
        ollama = _get_ollama()
        return ollama.answer(context=context, question=question, model=model, max_tokens=max_tokens, temperature=temperature)

    raise RuntimeError(f"No supported LLM provider configured (LLM_PROVIDER={provider})")