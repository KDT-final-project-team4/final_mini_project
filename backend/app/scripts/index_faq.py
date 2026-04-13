from __future__ import annotations

try:
    from app.config import settings
    from app.rag.embeddings import get_embedder
    from app.rag.faq_loader import load_faq_documents
    from app.rag.text_chunker import create_faq_chunks
    from app.rag.vector_store import FAQVectorStore
except ImportError:  # local test fallback
    from config import settings
    from rag.embeddings import get_embedder
    from rag.faq_loader import load_faq_documents
    from rag.text_chunker import create_faq_chunks
    from rag.vector_store import FAQVectorStore


def main() -> None:
    docs = load_faq_documents(settings.FAQ_DOCS_PATH)
    chunks = create_faq_chunks(
        docs,
        chunk_size=settings.FAQ_CHUNK_SIZE,
        chunk_overlap=settings.FAQ_CHUNK_OVERLAP,
    )

    embedder = get_embedder(settings.FAQ_EMBED_MODEL)
    store = FAQVectorStore(
        persist_dir=settings.FAQ_RAG_PERSIST_DIR,
        collection_name=settings.FAQ_RAG_COLLECTION_NAME,
    )

    result = store.upsert_chunks(chunks, embedder=embedder)

    print("=== FAQ INDEX RESULT ===")
    print(f"docs_path={settings.FAQ_DOCS_PATH}")
    print(f"document_count={len(docs)}")
    print(f"chunk_count={len(chunks)}")
    print(f"collection_name={settings.FAQ_RAG_COLLECTION_NAME}")
    print(f"persist_dir={settings.FAQ_RAG_PERSIST_DIR}")
    print(f"embed_model={settings.FAQ_EMBED_MODEL}")
    print(f"result={result}")
    print(f"collection_count={store.count()}")


if __name__ == "__main__":
    main()