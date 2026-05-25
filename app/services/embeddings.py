from typing import List
import re
import time
from google import genai


class EmbeddingService:
    def __init__(self, api_key: str, model_name: str = "gemini-embedding-001"):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate_embedding(self, text: str) -> List[float]:
        response = self._embed_with_retry([text], task_type="RETRIEVAL_QUERY")
        return response[0]

    def generate_embeddings(self, list_of_chunks: List[str]) -> List[List[float]]:
        vectors: List[List[float]] = []
        batch_size = 25
        for i in range(0, len(list_of_chunks), batch_size):
            batch = list_of_chunks[i : i + batch_size]
            vectors.extend(self._embed_with_retry(batch, task_type="RETRIEVAL_DOCUMENT"))
        return vectors

    def _embed_with_retry(self, contents: List[str], task_type: str) -> List[List[float]]:
        attempts = 0
        while True:
            try:
                response = self.client.models.embed_content(
                    model=self.model_name,
                    contents=contents,
                    config={"task_type": task_type},
                )
                return [item.values for item in response.embeddings]
            except Exception as exc:
                attempts += 1
                msg = str(exc)
                if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                    # Gemini often returns "Please retry in 24.7s".
                    match = re.search(r"retry in ([0-9]+(?:\\.[0-9]+)?)s", msg, re.IGNORECASE)
                    delay = float(match.group(1)) if match else min(30, 2 * attempts)
                    time.sleep(delay + 1)
                    continue
                raise
