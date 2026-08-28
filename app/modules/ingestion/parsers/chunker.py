"""Semantic text chunking for document indexing and RAG.

Uses langchain's RecursiveCharacterTextSplitter when available, falls back to
CharacterTextSplitter when that's the only option, and provides an internal
fallback implementation if LangChain is not installed.
"""

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


# Try to import LangChain splitters with fallbacks
_RecursiveSplitter = None
_CharacterSplitter = None
try:
    # Preferred: modern standalone package (LangChain >= 0.2)
    from langchain_text_splitters import RecursiveCharacterTextSplitter  # type: ignore
    _RecursiveSplitter = RecursiveCharacterTextSplitter
except Exception:
    try:
        # Older/alternate location, may still exist as a compatibility shim
        from langchain.text_splitter import RecursiveCharacterTextSplitter  # type: ignore
        _RecursiveSplitter = RecursiveCharacterTextSplitter
    except Exception:
        try:
            from langchain_text_splitters import CharacterTextSplitter  # type: ignore
            _CharacterSplitter = CharacterTextSplitter
        except Exception:
            try:
                from langchain.text_splitter import CharacterTextSplitter  # type: ignore
                _CharacterSplitter = CharacterTextSplitter
            except Exception:
                _RecursiveSplitter = None
                _CharacterSplitter = None

if _RecursiveSplitter is not None:
    logger.info("Chunker: using LangChain RecursiveCharacterTextSplitter")
elif _CharacterSplitter is not None:
    logger.info("Chunker: using LangChain CharacterTextSplitter")
else:
    logger.warning("Chunker: no LangChain text splitter available; using internal fallback chunker")


# Wrapper implementation that normalizes splitter usage
class _LangChainSplitterWrapper:
    def __init__(self, separators: List[str], chunk_size: int, chunk_overlap: int):
        # Prefer the recursive splitter if available because it accepts separators
        if _RecursiveSplitter is not None:
            # Many versions accept separators=..., chunk_size=..., chunk_overlap=..., length_function=...
            try:
                self._impl = _RecursiveSplitter(
                    separators=separators,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    length_function=len,
                )
                self._type = "recursive"
            except TypeError:
                # Older/alternate signature; try positional fallback
                self._impl = _RecursiveSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
                self._type = "recursive"
        elif _CharacterSplitter is not None:
            # CharacterTextSplitter usually only accepts chunk_size and chunk_overlap
            try:
                # instantiate with explicit args
                self._impl = _CharacterSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            except TypeError:
                # last-resort: try positional
                self._impl = _CharacterSplitter(chunk_size, chunk_overlap)
            self._type = "character"
        else:
            raise RuntimeError("No LangChain splitter available")

    def split_text(self, text: str) -> List[str]:
        # Delegate to LangChain implementation which should expose split_text
        return self._impl.split_text(text)


# Internal fallback splitter (recursive split, THEN merge small pieces back up
# to chunk_size with overlap - mirrors what LangChain's real splitter does).
class _FallbackSplitter:
    def __init__(self, separators: List[str], chunk_size: int, chunk_overlap: int):
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _split_on_separators(self, text: str, separators: List[str]) -> List[str]:
        """Recursively break text down into small atomic pieces using the
        separator hierarchy. Does NOT merge - that happens in a separate pass."""
        text = text.strip()
        if not text:
            return []
        if not separators:
            return [text]

        sep = separators[0]
        rest = separators[1:]

        if sep == "":
            # Last resort: no separator left, hard-slice by character.
            return [text[i:i + self.chunk_size] for i in range(0, len(text), self.chunk_size)]

        if sep not in text:
            return self._split_on_separators(text, rest)

        raw_parts = text.split(sep)
        pieces: List[str] = []
        for part in raw_parts:
            part = part.strip()
            if not part:
                continue
            if len(part) <= self.chunk_size:
                pieces.append(part)
            else:
                pieces.extend(self._split_on_separators(part, rest))
        return pieces

    def _merge_pieces(self, pieces: List[str]) -> List[str]:
        """Greedily merge small adjacent pieces into chunks close to
        chunk_size, keeping some overlap between consecutive chunks so
        context isn't lost at chunk boundaries."""
        if not pieces:
            return []

        chunks: List[str] = []
        current: List[str] = []
        current_len = 0

        for piece in pieces:
            piece_len = len(piece)
            joiner_len = 1 if current else 0  # space between joined pieces

            if current and current_len + joiner_len + piece_len > self.chunk_size:
                chunks.append(" ".join(current).strip())

                # Build overlap: keep trailing pieces whose combined length <= chunk_overlap
                overlap: List[str] = []
                overlap_len = 0
                for prev in reversed(current):
                    add_len = len(prev) + (1 if overlap else 0)
                    if overlap_len + add_len > self.chunk_overlap:
                        break
                    overlap.insert(0, prev)
                    overlap_len += add_len

                current = overlap
                current_len = overlap_len

            current.append(piece)
            current_len += piece_len + (1 if current_len else 0)

        if current:
            chunks.append(" ".join(current).strip())

        return [c for c in chunks if c]

    def split_text(self, text: str) -> List[str]:
        try:
            pieces = self._split_on_separators(text, self.separators)
            merged = self._merge_pieces(pieces)
            return [c.strip() for c in merged if c and c.strip()]
        except Exception:
            logger.exception("Fallback chunker failed; returning whole text as single chunk")
            return [text.strip()]


# Decide which splitter implementation to use at runtime
def _get_splitter_impl(separators: List[str], chunk_size: int, chunk_overlap: int):
    if _RecursiveSplitter is not None or _CharacterSplitter is not None:
        try:
            return _LangChainSplitterWrapper(separators=separators, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        except Exception as e:
            logger.warning("LangChain splitter import found but instantiation failed: %s. Falling back.", e)
            return _FallbackSplitter(separators=separators, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    else:
        return _FallbackSplitter(separators=separators, chunk_size=chunk_size, chunk_overlap=chunk_overlap)


class SemanticChunker:
    """
    Split extracted text into semantic chunks for RAG indexing.

    Parameters:
    - chunk_size: max characters per chunk
    - chunk_overlap: overlap characters between chunks
    - separators: prioritized separators for recursive splitting
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separators: Optional[List[str]] = None
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]
        self.splitter = _get_splitter_impl(self.separators, self.chunk_size, self.chunk_overlap)

    def chunk(self, text: str, metadata: Dict = None) -> List[Dict[str, Any]]:
        """
        Split text into semantic chunks.

        Returns a list of dicts:
        {
            "chunk_id": "chunk_1",
            "text": "...",
            "chunk_num": 1,
            "total_chunks": N,
            "metadata": {...}
        }
        """
        if not text or not text.strip():
            logger.warning("Empty text provided to chunker")
            return []

        try:
            splits = self.splitter.split_text(text)
            chunks: List[Dict[str, Any]] = []
            total = len(splits)
            for i, chunk_text in enumerate(splits, 1):
                chunks.append({
                    "chunk_id": f"chunk_{i}",
                    "text": chunk_text,
                    "chunk_num": i,
                    "total_chunks": total,
                    "metadata": metadata or {}
                })
            logger.info("Chunked text into %d semantic chunks", len(chunks))
            return chunks
        except Exception:
            logger.exception("Chunking failed")
            raise

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Rough token estimate (approx 4 characters per token)."""
        return len(text) // 4
