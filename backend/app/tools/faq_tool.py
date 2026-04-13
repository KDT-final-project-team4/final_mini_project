from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, TypedDict

try:
    from app.config import get_logger, settings
    from app.rag.answer_generator import generate_faq_answer
    from app.rag.embeddings import get_embedder
    from app.rag.faq_loader import load_faq_documents
    from app.rag.retriever import retrieve_faq_hits
    from app.rag.text_chunker import create_faq_chunks
    from app.rag.vector_store import FAQVectorStore
except ImportError:  # local test fallback
    from config import get_logger, settings
    from rag.answer_generator import generate_faq_answer
    from rag.embeddings import get_embedder
    from rag.faq_loader import load_faq_documents
    from rag.retriever import retrieve_faq_hits
    from rag.text_chunker import create_faq_chunks
    from rag.vector_store import FAQVectorStore


logger = get_logger(__name__)


class FAQToolResult(TypedDict):
    success: bool
    tool_name: str
    message: str
    data: dict[str, Any]
    error: Optional[str]


MOCK_FAQ = {
    "운영시간": {
        "matched_topic": "operating_hours",
        "answer": "운영시간은 09:00~18:00 입니다.",
    },
    "영업시간": {
        "matched_topic": "operating_hours",
        "answer": "운영시간은 09:00~18:00 입니다.",
    },
    "상담": {
        "matched_topic": "callback_guide",
        "answer": "상담이 필요하시면 콜백 요청을 남겨주세요.",
    },
    "전화": {
        "matched_topic": "callback_guide",
        "answer": "전화 상담은 콜백 요청을 통해 접수할 수 있습니다.",
    },
    "사진": {
        "matched_topic": "vision_guide",
        "answer": "사진을 함께 보내주시면 더 정확하게 확인할 수 있습니다.",
    },
}


def _success_result(
    *,
    answer: str,
    original_query: str,
    matched_topic: str,
    mode: str,
    sources: list[dict[str, Any]] | None = None,
    retrieved_count: int = 0,
) -> FAQToolResult:
    return {
        "success": True,
        "tool_name": "faq",
        "message": "FAQ 조회 성공",
        "data": {
            "matched_topic": matched_topic,
            "answer": answer,
            "original_query": original_query,
            "mode": mode,
            "retrieved_count": retrieved_count,
            "sources": sources or [],
        },
        "error": None,
    }


def _failure_result(query: str, error: str) -> FAQToolResult:
    return {
        "success": False,
        "tool_name": "faq",
        "message": "FAQ 조회 실패",
        "data": {
            "matched_topic": "faq_error",
            "answer": "FAQ 처리 중 문제가 발생했습니다.",
            "original_query": query.strip(),
        },
        "error": error,
    }


def _mock_search(clean_query: str) -> FAQToolResult:
    if not clean_query:
        return _failure_result(clean_query, "질문이 비어 있습니다.")

    for keyword, payload in MOCK_FAQ.items():
        if keyword in clean_query:
            return _success_result(
                answer=payload["answer"],
                original_query=clean_query,
                matched_topic=payload["matched_topic"],
                mode="mock",
            )

    return _success_result(
        answer="현재 등록된 FAQ에서 정확한 답변을 찾지 못했어요. 질문을 조금 더 구체적으로 말씀해주세요.",
        original_query=clean_query,
        matched_topic="not_found",
        mode="mock",
    )


def _ensure_index_exists() -> None:
    store = FAQVectorStore(
        persist_dir=settings.FAQ_RAG_PERSIST_DIR,
        collection_name=settings.FAQ_RAG_COLLECTION_NAME,
    )

    if store.count() > 0:
        return

    docs_path = Path(settings.FAQ_DOCS_PATH)
    if not docs_path.exists():
        raise FileNotFoundError(f"FAQ docs file not found: {docs_path}")

    docs = load_faq_documents(docs_path)
    chunks = create_faq_chunks(
        docs,
        chunk_size=settings.FAQ_CHUNK_SIZE,
        chunk_overlap=settings.FAQ_CHUNK_OVERLAP,
    )
    embedder = get_embedder(settings.FAQ_EMBED_MODEL)
    result = store.upsert_chunks(chunks, embedder=embedder)

    logger.info("faq_tool.index_built result=%s", result)


def _rag_search(clean_query: str) -> FAQToolResult:
    if not clean_query:
        return _failure_result(clean_query, "질문이 비어 있습니다.")

    _ensure_index_exists()

    hits = retrieve_faq_hits(clean_query, top_k=settings.FAQ_RAG_TOP_K)
    answer_payload = generate_faq_answer(clean_query, hits)

    sources: list[dict[str, Any]] = []
    for hit in hits:
        metadata = hit.get("metadata") or {}
        sources.append(
            {
                "rank": hit.get("rank"),
                "question": metadata.get("question"),
                "category": metadata.get("category"),
                "source_id": metadata.get("source_id"),
                "distance": hit.get("distance"),
                "text": hit.get("text"),
            }
        )

    matched_topic = "faq_rag"
    if sources:
        matched_topic = str(sources[0].get("source_id") or "faq_rag")

    return _success_result(
        answer=answer_payload["answer"],
        original_query=clean_query,
        matched_topic=matched_topic,
        mode=answer_payload.get("mode", "extractive"),
        sources=sources,
        retrieved_count=len(hits),
    )


def faq_tool(query: str) -> FAQToolResult:
    clean_query = query.strip()
    mode = settings.FAQ_MODE

    logger.info("faq_tool.enter mode=%s query=%s", mode, clean_query)

    try:
        if mode == "rag":
            result = _rag_search(clean_query)
        else:
            result = _mock_search(clean_query)

        logger.info(
            "faq_tool.exit success=%s mode=%s retrieved_count=%s",
            result.get("success"),
            (result.get("data") or {}).get("mode"),
            (result.get("data") or {}).get("retrieved_count"),
        )
        return result

    except Exception as exc:
        logger.exception("faq_tool.exception error=%s", exc)
        return _failure_result(clean_query, f"FAQ 처리 중 오류가 발생했습니다: {exc}")


if __name__ == "__main__":
    print(faq_tool("운영시간 알려줘"))
    print(faq_tool("상담은 어떻게 하나요?"))
    print(faq_tool("사진으로 문의해도 되나요?"))