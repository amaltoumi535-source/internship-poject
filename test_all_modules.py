import requests
import sys

BASE = "http://localhost:8000"
TEST_FILE = "test_doc.txt"  # a small text file with real content

results = []

def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    results.append((name, status, detail))
    print(f"[{status}] {name} {detail}")

# 0. Create a small test file if it doesn't exist
import os
if not os.path.exists(TEST_FILE):
    with open(TEST_FILE, "w", encoding="utf-8") as f:
        f.write("Apple was founded by Steve Jobs in Cupertino, California. "
                 "The company designs consumer electronics, software, and services.")

# 1. INGESTION
with open(TEST_FILE, "rb") as f:
    r = requests.post(f"{BASE}/ingest/", files={"file": f})
check("Ingestion (/ingest/)", r.status_code == 200, f"status={r.status_code}")
doc_id = None
if r.status_code == 200:
    data = r.json()
    doc_id = data.get("document_id")
    check("  -> chunks_count > 0", data.get("chunks_count", 0) > 0, f"chunks={data.get('chunks_count')}")
else:
    print(r.text)

# 2. STORAGE (via reporting export, since storage has no dedicated route)
r = requests.get(f"{BASE}/reports/export?format=json")
check("Storage (doc appears in export)", r.status_code == 200 and doc_id and any(
    row.get("id") == doc_id for row in r.json().get("rows", [])
), f"status={r.status_code}")

# 3. ANALYSIS
r = requests.post(f"{BASE}/analyze/text", json={
    "text": "Apple was founded by Steve Jobs in Cupertino, California.",
    "extract_entities": True,
    "readability": True
})
if r.status_code == 200:
    d = r.json()
    check("Analysis - language detection", bool(d.get("language", {}).get("language")))
    check("Analysis - entity extraction", len(d.get("entities", [])) > 0)
    check("Analysis - readability", bool(d.get("readability")))
else:
    check("Analysis (/analyze/text)", False, f"status={r.status_code}")

if doc_id:
    r = requests.post(f"{BASE}/analyze/document/{doc_id}", json={
        "summarize_chunks": False,
        "summarize_document": True,
        "detect_language": True,
        "extract_entities": True
    })
    check("Analysis - /analyze/document/{id}", r.status_code == 200, f"status={r.status_code}")

# 4. SEARCH
r = requests.get(f"{BASE}/search/", params={"q": "Apple"})
check("Search (/search/?q=Apple)", r.status_code == 200 and r.json().get("total", 0) > 0, f"status={r.status_code}")

# 5. REPORTING
r = requests.get(f"{BASE}/reports/overview")
check("Reporting - overview", r.status_code == 200 and r.json().get("total_documents", 0) > 0)

if doc_id:
    r = requests.get(f"{BASE}/reports/doc/{doc_id}")
    check("Reporting - doc/{id}", r.status_code == 200)

r = requests.get(f"{BASE}/reports/export?format=json")
check("Reporting - export", r.status_code == 200 and len(r.json().get("rows", [])) > 0)

# SUMMARY
print("\n--- SUMMARY ---")
passed = sum(1 for _, s, _ in results if s == "PASS")
print(f"{passed}/{len(results)} checks passed")
for name, status, detail in results:
    if status == "FAIL":
        print(f"  FAILED: {name} {detail}")