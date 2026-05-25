from typing import List
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def generate_embedding(self, text: str) -> List[float]:
        return self.model.encode(text, normalize_embeddings=True).tolist()

    def generate_embeddings(self, list_of_chunks: List[str]) -> List[List[float]]:
        return self.model.encode(list_of_chunks, normalize_embeddings=True).tolist()
