import os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.rag.retriever import HybridRetriever

CASES = [
    ("What is the refund window?", "company_policy.txt"),
    ("When can customers contact support?", "company_policy.txt"),
    ("What is the password security rule?", "company_policy.txt"),
]

if __name__ == "__main__":
    retriever = HybridRetriever()
    hits = 0
    for question, expected_source in CASES:
        results = retriever.retrieve(question, limit=3)
        ok = any(r.get("document_name") == expected_source for r in results)
        hits += int(ok)
        print(f"{'PASS' if ok else 'FAIL'} | {question}")
    print(f"retrieval_source_hit_rate={hits/len(CASES):.2%}")
