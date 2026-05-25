import faiss
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple


class FaissVectorStore:
    def __init__(self, vector_dim: int, index_path: str = "faiss.index", meta_path: str = "faiss_meta.json"):
        self.vector_dim = vector_dim
        self.index_path = Path(index_path)
        self.meta_path = Path(meta_path)
        self.index = self.create_index()
        self.metadata: List[Dict] = []
        self._load_if_exists()

    def create_index(self):
        return faiss.IndexFlatIP(self.vector_dim)

    def add_documents(self, vectors: List[List[float]], metadata: List[Dict]) -> None:
        if not vectors:
            return
        arr = np.array(vectors, dtype="float32")
        self.index.add(arr)
        self.metadata.extend(metadata)

    def search(self, query_embedding: List[float], top_k: int = 3) -> List[Tuple[float, Dict]]:
        if self.index.ntotal == 0:
            return []
        q = np.array([query_embedding], dtype="float32")
        scores, indices = self.index.search(q, top_k)
        out = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1 or idx >= len(self.metadata):
                continue
            out.append((float(score), self.metadata[idx]))
        return out

    def persist(self) -> None:
        faiss.write_index(self.index, str(self.index_path))
        self.meta_path.write_text(json.dumps(self.metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    def _load_if_exists(self) -> None:
        if self.index_path.exists() and self.meta_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            self.metadata = json.loads(self.meta_path.read_text(encoding="utf-8"))
