from typing import Dict, List


class RetrievalService:
    def __init__(self, embedder, vector_store, threshold: float = 0.12, top_k: int = 5):
        self.embedder = embedder
        self.vector_store = vector_store
        self.threshold = threshold
        self.top_k = top_k

    def retrieve(self, query: str) -> List[Dict]:
        query_embedding = self.embedder.generate_embedding(query)
        results = self.vector_store.search(query_embedding, top_k=self.top_k)
        return [{"chunk": item["content"], "score": round(score, 4), "metadata": item} for score, item in results]

    def apply_threshold(self, results: List[Dict]) -> List[Dict]:
        return [r for r in results if r["score"] >= self.threshold]
