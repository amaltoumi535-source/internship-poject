from app.modules.analysis.service import AnalysisService
from app.modules.storage.vectorstore import VectorStoreAdapter

print("Loading embedding model (first run downloads it from Hugging Face)...")
analysis = AnalysisService()
embeddings = analysis.embed_texts([
    "The sky is blue.",
    "Cats are mammals.",
    "Paris is the capital of France.",
])
print(f"Generated {len(embeddings)} embeddings, dimension: {len(embeddings[0])}")

print("Testing ChromaDB adapter...")
store = VectorStoreAdapter()
store.upsert("test_collection", [
    {"id": "1", "embedding": embeddings[0], "metadata": {"source": "test"}, "document_text": "The sky is blue."},
    {"id": "2", "embedding": embeddings[1], "metadata": {"source": "test"}, "document_text": "Cats are mammals."},
    {"id": "3", "embedding": embeddings[2], "metadata": {"source": "test"}, "document_text": "Paris is the capital of France."},
])
print("Upsert succeeded.")

query_embedding = analysis.embed_texts(["What is the capital of France?"])[0]
results = store.query("test_collection", query_embedding, top_k=2)
print("Query results:", results)
