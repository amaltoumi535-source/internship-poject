"""
Test semantic vs literal search tools directly.
This isolates the search logic from agents, showing raw tool behavior.
"""

from app.modules.search.agent import (
    search_chunks_tool,
    semantic_search_tool,
)

test_queries = [
    ("supplier performance metrics", "exact term both should match"),
    ("how do we manage vendor relationships?", "semantic should find results even without exact phrase"),
    ("risk mitigation strategies", "semantic search for concepts"),
]

print("=" * 80)
print("COMPARING LITERAL vs SEMANTIC SEARCH")
print("=" * 80)

for query, description in test_queries:
    print(f"\n{chr(8212) * 80}")
    print(f"Query: '{query}'")
    print(f"Intent: {description}")
    print(f"{chr(8212) * 80}")

    literal_count = 0
    semantic_count = 0

    print("\n1) LITERAL SEARCH (LIKE)")
    try:
        literal_result = search_chunks_tool.invoke({"query": query, "limit": 3})
        literal_count = literal_result.get("total", 0)
        print(f"   Found: {literal_count} chunks")
        if literal_result.get("results"):
            for i, result in enumerate(literal_result["results"][:2], 1):
                # Literal search uses "snippet" as its content field, not "text" -
                # different schema from semantic search's results, by design.
                text_preview = result.get("snippet", "")[:100].replace("\n", " ")
                print(f"   [{i}] {text_preview}...")
        else:
            print("   (no results)")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n2) SEMANTIC SEARCH (Vectorial)")
    try:
        semantic_result = semantic_search_tool.invoke({"query": query, "top_k": 3})
        semantic_count = semantic_result.get("total", 0)
        print(f"   Found: {semantic_count} chunks")
        if semantic_result.get("results"):
            for i, result in enumerate(semantic_result["results"][:2], 1):
                text_preview = result.get("text", "")[:100].replace("\n", " ")
                similarity = result.get("similarity_score", 0)
                print(f"   [{i}] (similarity: {similarity:.3f}) {text_preview}...")
        else:
            print("   (no results)")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\nComparison:")
    if literal_count == 0 and semantic_count > 0:
        print("   SEMANTIC FOUND RESULTS WHERE LITERAL FAILED -> semantic is adding value here")
    elif literal_count > 0 and semantic_count == 0:
        print("   LITERAL FOUND, SEMANTIC DIDN'T -> may indicate an issue with embeddings/ChromaDB")
    elif literal_count > 0 and semantic_count > 0:
        print("   BOTH FOUND RESULTS -> good for hybrid search, agent can choose best strategy")
    else:
        print("   NEITHER FOUND RESULTS -> query may not match any documents")

print("\n" + "=" * 80)
print("Test Complete")
print("=" * 80)
