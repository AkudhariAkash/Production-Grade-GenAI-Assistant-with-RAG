import json
from typing import Dict, List


def load_documents(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def chunk_text(text: str, chunk_size_tokens: int = 350) -> List[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size_tokens):
        chunks.append(" ".join(words[i:i + chunk_size_tokens]))
    return chunks


def build_chunks(documents: List[Dict], source: str = "docs.json") -> List[Dict]:
    items = []
    chunk_id = 1
    for doc in documents:
        for chunk in chunk_text(doc["content"], chunk_size_tokens=350):
            items.append({
                "chunk_id": str(chunk_id),
                "title": doc["title"],
                "content": chunk,
                "embedding_text": f"Title: {doc['title']}\nContent: {chunk}",
                "source": source,
                "source_document": doc["title"]
            })
            chunk_id += 1
    return items
