from app.modules.search.chromadb_adapter import ChromaDBAdapter

adapter = ChromaDBAdapter()
results = adapter.search("test", top_k=10)

print(f"Total documents in ChromaDB: {len(results)}")
if results:
    for i, r in enumerate(results):
        print(f"\n{i+1}. {r['content'][:100]}...")
else:
    print("❌ NO DOCUMENTS IN CHROMADB!")