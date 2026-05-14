# test_rag.py
from vectorstore.chroma_store import vectorstore

results = vectorstore.similarity_search("what is diabetes", k=3)
print(f"Found {len(results)} chunks")
for r in results:
    print(r.page_content[:200])
    print("---")