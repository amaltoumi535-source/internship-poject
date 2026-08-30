# app/modules/llm/factory.py
"""
LLM factory - creates the appropriate LLM instance based on configuration.
Supports: Anthropic, OpenAI, Groq, Ollama.
"""

from typing import Optional

from app.config import get_settings
from app.modules.infrastructure.logger import get_logger

logger = get_logger(__name__)


def get_llm():
    """
    Factory function to get the configured LLM instance.
    Returns the appropriate LLM based on LLM_PROVIDER setting.
    """
    settings = get_settings()
    provider = settings.llm_provider.lower()

    try:
        if provider == "anthropic":
            return get_anthropic_llm(settings)
        elif provider == "openai":
            return get_openai_llm(settings)
        elif provider == "groq":
            return get_groq_llm(settings)
        elif provider == "ollama":
            return get_ollama_llm(settings)
        else:
            logger.warning(f"Unknown LLM provider: {provider}, defaulting to Anthropic")
            return get_anthropic_llm(settings)
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        raise


def get_anthropic_llm(settings):
    """Initialize Anthropic Claude LLM."""
    try:
        from langchain_anthropic import ChatAnthropic

        api_key = settings.anthropic_api_key
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")

        return ChatAnthropic(
            api_key=api_key,
            model=settings.anthropic_model,
            temperature=0.7,
            max_retries=3,
        )
    except ImportError:
        raise ImportError("langchain-anthropic not installed")


def get_openai_llm(settings):
    """Initialize OpenAI GPT LLM."""
    try:
        from langchain_openai import ChatOpenAI

        api_key = settings.openai_api_key
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")

        return ChatOpenAI(
            api_key=api_key,
            model=settings.openai_model,
            temperature=0.7,
            max_retries=3,
        )
    except ImportError:
        raise ImportError("langchain-openai not installed")


def get_groq_llm(settings):
    """Initialize Groq LLM."""
    try:
        from langchain_groq import ChatGroq

        api_key = settings.groq_api_key
        if not api_key:
            raise ValueError("GROQ_API_KEY not set")

        return ChatGroq(
            api_key=api_key,
            model=settings.groq_model,
            temperature=0.7,
            max_retries=3,
        )
    except ImportError:
        raise ImportError("langchain-groq not installed")


def get_ollama_llm(settings):
    """Initialize Ollama local LLM."""
    try:
        from langchain_community.llms import Ollama

        if not settings.ollama_model:
            raise ValueError("OLLAMA_MODEL not set")

        return Ollama(
            base_url=settings.ollama_url or "http://localhost:11434",
            model=settings.ollama_model,
            temperature=0.7,
        )
    except ImportError:
        raise ImportError("langchain-community not installed")
