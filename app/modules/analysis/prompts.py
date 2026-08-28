"""Prompt templates for optional LLM-based summarization / analysis.

These are lightweight templates to be used if you later wire an LLM (OpenAI / local).
"""

SINGLE_DOC_SUMMARY = """You are an assistant that summarizes documents concisely.

Document:
{document_text}

Provide a short summary in 2-4 sentences preserving meaning and important facts.
Summary:
"""

CHUNK_SUMMARY = """You are an assistant that summarizes short text chunks.

Chunk:
{chunk_text}

Provide a single-sentence summary of this chunk.
Summary:
"""