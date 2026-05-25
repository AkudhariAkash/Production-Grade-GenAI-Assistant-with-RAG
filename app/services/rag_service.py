import os
from typing import Any, Dict

from dotenv import load_dotenv
from app.prompts.prompt_template import FALLBACK_RESPONSE, PROMPT_TEMPLATE, RELATED_FALLBACK_PROMPT
from app.services.chat_store import ChatHistoryStore
from app.services.embeddings import EmbeddingService
from app.services.ingestion import build_chunks, load_documents
from app.services.llm_service import LLMService
from app.services.memory import InMemorySessionMemory
from app.services.retrieval import RetrievalService
from app.utils.logger import setup_logger
from app.vectorstore.vector_store import FaissVectorStore


class RAGService:
    def __init__(self, docs_path: str = "docs.json"):
        load_dotenv()
        for proxy_key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
            proxy_val = os.getenv(proxy_key, "").strip().lower()
            if proxy_val in {"http://127.0.0.1:9", "https://127.0.0.1:9"}:
                os.environ.pop(proxy_key, None)
        self.logger = setup_logger()
        self.docs_path = docs_path
        self.embedder = EmbeddingService("all-MiniLM-L6-v2")
        self.memory = InMemorySessionMemory(max_pairs=5)
        self.chat_store = ChatHistoryStore("chat_history.db")
        similarity_threshold = float(os.getenv("SIMILARITY_THRESHOLD", "0.12"))
        top_k = int(os.getenv("TOP_K", "5"))

        dim = len(self.embedder.generate_embedding("probe"))
        self.vector_store = FaissVectorStore(vector_dim=dim)
        self.retrieval = RetrievalService(
            self.embedder,
            self.vector_store,
            threshold=similarity_threshold,
            top_k=top_k,
        )

        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("Please set GEMINI_API_KEY in environment")
        self.llm = LLMService(api_key=api_key)
        self._ensure_index()

    def _ensure_index(self):
        documents = load_documents(self.docs_path)
        chunks = build_chunks(documents, source=self.docs_path)
        needs_rebuild = True

        if self.vector_store.index.ntotal > 0:
            same_count = (
                self.vector_store.index.ntotal == len(chunks)
                and len(self.vector_store.metadata) == len(chunks)
            )
            has_embedding_text = all("embedding_text" in item for item in self.vector_store.metadata)
            if same_count and has_embedding_text:
                needs_rebuild = False
                self.logger.info("Loaded FAISS index with %d vectors", self.vector_store.index.ntotal)
            else:
                self.logger.info(
                    "Rebuilding stale FAISS index (index=%d, docs=%d, title-aware=%s)",
                    self.vector_store.index.ntotal,
                    len(chunks),
                    has_embedding_text,
                )

        if needs_rebuild:
            self.vector_store.index = self.vector_store.create_index()
            self.vector_store.metadata = []
            vectors = self.embedder.generate_embeddings([c["embedding_text"] for c in chunks])
            self.vector_store.add_documents(vectors, chunks)
            self.vector_store.persist()
            self.retrieval.vector_store = self.vector_store
            self.logger.info("Built FAISS index with %d chunks", len(chunks))

    def chat(self, session_id: str, message: str) -> Dict[str, Any]:
        self.logger.info("User query | session=%s | q=%s", session_id, message)
        retrieved = self.retrieval.retrieve(message)
        filtered = self.retrieval.apply_threshold(retrieved)
        self.logger.info("Similarity scores: %s", [r["score"] for r in retrieved])

        if not retrieved:
            return {
                "reply": FALLBACK_RESPONSE,
                "tokensUsed": 0,
                "retrievedChunks": 0,
                "similarityScores": [r["score"] for r in retrieved],
                "responseTimeMs": 0,
            }
        context_source = filtered if filtered else retrieved[: min(3, len(retrieved))]
        context = "\n\n".join([
            f"[{r['metadata']['title']} | chunk={r['metadata']['chunk_id']} | score={r['score']}]\n{r['chunk']}" for r in context_source
        ])

        persistent = self.chat_store.get_recent(session_id, limit=5)
        memory = self.memory.get_history(session_id)
        history = (persistent + memory)[-5:]
        history_text = "\n".join([f"User: {h['user']}\nAssistant: {h['assistant']}" for h in history]) or "No prior conversation"

        if filtered:
            prompt = PROMPT_TEMPLATE.format(retrieved_context=context, history=history_text, user_question=message)
        else:
            prompt = RELATED_FALLBACK_PROMPT.format(retrieved_context=context, user_question=message)
        reply, tokens, latency_ms = self.llm.generate(prompt)

        self.memory.add_turn(session_id, message, reply)
        self.chat_store.save_turn(session_id, message, reply)

        return {
            "reply": reply,
            "tokensUsed": tokens,
            "retrievedChunks": len(context_source),
            "similarityScores": [r["score"] for r in retrieved],
            "responseTimeMs": latency_ms,
        }
