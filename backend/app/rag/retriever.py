from __future__ import annotations

from functools import lru_cache

try:
    from app.config import settings
except ImportError:  # local test fallback
    from config import settings

from app.rag.embeddings import FAQEmbedder, get_embedder
from app.rag.vector_store import FAQVectorStore


@lru_cache(maxsize=4)
def get_faq_vector_store() -> FAQVectorStore:
    return FAQVectorStore(
        persist_dir=settings.FAQ_RAG_PERSIST_DIR,
        collection_name=settings.FAQ_RAG_COLLECTION_NAME,
    )


@lru_cache(maxsize=4)
def get_faq_embedder() -> FAQEmbedder:
    return get_embedder(settings.FAQ_EMBED_MODEL)


def retrieve_faq_hits(query: str, top_k: int = 3) -> list[dict]:
    store = get_faq_vector_store()
    embedder = get_faq_embedder()
    return store.query(query, embedder=embedder, top_k=top_k)