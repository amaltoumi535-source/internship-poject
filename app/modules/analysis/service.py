"""AnalysisService: language detection, summarization, entity extraction, chunk scoring."""

from typing import List, Optional, Dict, Any
import logging
import re

logger = logging.getLogger(__name__)


def _split_sentences(text: str) -> List[str]:
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s and s.strip()]
    return sentences


class AnalysisService:
    """
    High-level analysis utilities. Uses optional libraries only when requested.
    """

    def __init__(self, embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.embedding_model_name = embedding_model_name
        self._embedder = None  # lazy

    # Extractive summarization (frequency-based)
    def summarize_extractive(self, text: str, ratio: float = 0.2) -> str:
        if not text or len(text.split()) < 30:
            return text.strip()

        sentences = _split_sentences(text)
        if not sentences:
            return text.strip()

        words = re.findall(r"\w+", text.lower())
        freq: Dict[str, int] = {}
        for w in words:
            freq[w] = freq.get(w, 0) + 1

        sent_scores: List[float] = []
        for s in sentences:
            s_words = re.findall(r"\w+", s.lower())
            if not s_words:
                sent_scores.append(0.0)
                continue
            score = sum(freq.get(w, 0) for w in s_words) / len(s_words)
            sent_scores.append(score)

        n_select = max(1, int(len(sentences) * ratio))
        top_idx = sorted(range(len(sentences)), key=lambda i: sent_scores[i], reverse=True)[:n_select]
        top_idx_sorted = sorted(top_idx)
        summary = " ".join(sentences[i] for i in top_idx_sorted)
        return summary.strip()

    # Language detection
    def detect_language(self, text: str) -> Dict[str, Any]:
        try:
            from langdetect import detect_langs  # type: ignore
            probs = detect_langs(text)
            if not probs:
                return {"language": None, "confidence": None}
            top = probs[0]
            return {"language": top.lang, "confidence": float(top.prob)}
        except Exception:
            logger.warning("langdetect not available or failed", exc_info=True)
            return {"language": None, "confidence": None}

    # Entity extraction via spaCy
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        try:
            import spacy  # type: ignore
            try:
                nlp = spacy.load("en_core_web_sm")
            except Exception:
                logger.warning("spaCy model 'en_core_web_sm' not found; falling back to blank pipeline (no entities will be detected)", exc_info=True)
                nlp = spacy.blank("en")
            doc = nlp(text)
            entities = []
            for ent in doc.ents:
                entities.append({"text": ent.text, "label": ent.label_, "start": ent.start_char, "end": ent.end_char})
            return entities
        except Exception:
            logger.warning("spaCy not available or failed", exc_info=True)
            return []

    # Readability metrics with textstat
    def readability(self, text: str) -> Dict[str, Any]:
        try:
            import textstat  # type: ignore
            return {
                "flesch_reading_ease": getattr(textstat, "flesch_reading_ease")(text),
                "flesch_kincaid_grade": getattr(textstat, "flesch_kincaid_grade")(text),
                "gunning_fog": getattr(textstat, "gunning_fog")(text),
                "smog_index": getattr(textstat, "smog_index")(text),
            }
        except Exception:
            logger.warning("textstat not available or failed", exc_info=True)
            return {}

    # Embeddings (sentence-transformers)
    def _ensure_embedder(self):
        if self._embedder is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
            self._embedder = SentenceTransformer(self.embedding_model_name)
        except Exception as exc:
            raise RuntimeError(
                "sentence-transformers is required for embeddings. Install with: pip install sentence-transformers"
            ) from exc

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        self._ensure_embedder()
        return self._embedder.encode(texts, show_progress_bar=False, convert_to_numpy=True).tolist()

    # Score chunks by a query using embeddings cosine similarity
    def score_chunks_by_query(self, chunk_texts: List[str], query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        import numpy as np  # type: ignore

        self._ensure_embedder()
        chunk_emb = self._embedder.encode(chunk_texts, show_progress_bar=False, convert_to_numpy=True)
        q_emb = self._embedder.encode([query], show_progress_bar=False, convert_to_numpy=True)[0]

        def _cos_sim(a, b):
            denom = (np.linalg.norm(a) * np.linalg.norm(b))
            if denom == 0:
                return 0.0
            return float(np.dot(a, b) / denom)

        scores = []
        for i, emb in enumerate(chunk_emb):
            scores.append({"index": i, "score": _cos_sim(emb, q_emb)})
        scores_sorted = sorted(scores, key=lambda x: x["score"], reverse=True)[:top_k]
        return scores_sorted

    # High-level analyze_text
    def analyze_text(self, text: str, summarize: bool = True, summary_ratio: float = 0.2,
                     detect_language: bool = True, extract_entities: bool = False,
                     readability: bool = False) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        out["summary"] = None
        if summarize:
            out["summary"] = {"summary": self.summarize_extractive(text, ratio=summary_ratio), "method": "extractive"}
        out["language"] = self.detect_language(text) if detect_language else {"language": None, "confidence": None}
        out["entities"] = self.extract_entities(text) if extract_entities else []
        out["readability"] = self.readability(text) if readability else {}
        return out

    # Analyze a persisted document by id (requires StorageRepository)
    def analyze_document(self, repo, document_id: int, opts: Dict[str, Any]) -> Dict[str, Any]:
        """
        repo: an instance of StorageRepository
        opts: dict matching AnalyzeDocumentRequest fields
        """
        doc = repo.get_document(document_id)
        if not doc:
            raise ValueError("document not found")

        chunks = getattr(doc, "chunks", []) or []
        chunk_texts = [c.text for c in chunks]
        # Summarize chunks
        chunk_summaries = []
        if opts.get("summarize_chunks"):
            for txt in chunk_texts:
                chunk_summaries.append(self.summarize_extractive(txt, ratio=0.2))
        else:
            chunk_summaries = [None] * len(chunk_texts)

        # Document-level summary
        doc_summary = None
        if opts.get("summarize_document"):
            joined = "\n\n".join(chunk_texts)
            doc_summary = self.summarize_extractive(joined, ratio=0.15)

        # Scores by query
        scores_map = {}
        query = opts.get("query")
        if query:
            scores = self.score_chunks_by_query(chunk_texts, query, top_k=opts.get("top_k_by_query") or 5)
            for s in scores:
                scores_map[s["index"]] = s["score"]

        # language & entities
        lang = None
        if opts.get("detect_language"):
            lang = self.detect_language(" ".join(chunk_texts))
        ents = []
        if opts.get("extract_entities"):
            ents = self.extract_entities(" ".join(chunk_texts))

        # Build result
        chunks_out = []
        for i, c in enumerate(chunks):
            preview = (c.text[:200] if c.text else "")
            chunks_out.append({
                "chunk_id": getattr(c, "chunk_id", None),
                "chunk_num": getattr(c, "chunk_num", None),
                "text_preview": preview,
                "summary": chunk_summaries[i],
                "score": scores_map.get(i),
            })

        return {
            "document_id": document_id,
            "document_filename": getattr(doc, "filename", None),
            "document_summary": doc_summary,
            "chunks": chunks_out,
            "language": lang,
            "entities": ents,
        }