from __future__ import annotations

from typing import Any, TypedDict

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from app.config import (
    EMBEDDING_MODEL,
    CHROMA_COLLECTION_NAME,
    CHROMA_PERSIST_DIRECTORY,
)


class RetrievedChunk(TypedDict, total=False):
    """
    개별 검색 근거(chunk) 구조.
    """

    content: str
    score: float | None
    source: str | None
    file_name: str | None
    file_type: str | None
    page: int | None
    chunk_index: int | None
    doc_type: str | None


class KnowledgeSearchResult(TypedDict, total=False):
    """
    검색 결과 전체 구조.
    """

    query: str
    search_type: str
    retrieved_count: int
    enough_evidence: bool
    results: list[RetrievedChunk]
    fallback_message: str | None


# --------------------------------------------------------------
# 전역 초기화
# --------------------------------------------------------------
# 서버 기동 시 1회만 로드해 재사용한다.
_embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

_vectorstore = Chroma(
    collection_name=CHROMA_COLLECTION_NAME,
    persist_directory=CHROMA_PERSIST_DIRECTORY,
    embedding_function=_embeddings,
)


def _normalize_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """
    벡터스토어에서 가져온 metadata를 표준 형태로 정리한다.
    """
    return {
        "source": metadata.get("source"),
        "file_name": metadata.get("file_name"),
        "file_type": metadata.get("file_type"),
        "page": metadata.get("page"),
        "chunk_index": metadata.get("chunk_index"),
        "doc_type": metadata.get("doc_type"),
    }


def knowledge_search_tool(
    query: str,
    top_k: int = 4,
    score_threshold: float = 0.15,
) -> KnowledgeSearchResult:
    """
    구조화된 문서 검색 도구.

    역할
    ----
    - query를 받아 ChromaDB에서 관련 chunk 검색
    - 결과를 구조화된 dict 형태로 반환
    - 근거 충분성에 대한 아주 1차적인 판단만 수행

    주의
    ----
    이 함수는 '최종 답변 생성'을 하지 않는다.
    검색만 담당한다.
    """
    cleaned_query = (query or "").strip()

    if not cleaned_query:
        return {
            "query": "",
            "search_type": "empty",
            "retrieved_count": 0,
            "enough_evidence": False,
            "results": [],
            "fallback_message": "검색할 질문이 비어 있습니다.",
        }

    try:
        # ----------------------------------------------------------
        # 1차: relevance score 포함 검색
        # ----------------------------------------------------------
        docs_with_scores = _vectorstore.similarity_search_with_relevance_scores(
            cleaned_query,
            k=top_k,
        )

        results: list[RetrievedChunk] = []

        for doc, score in docs_with_scores:
            metadata = _normalize_metadata(doc.metadata)

            results.append(
                {
                    "content": (doc.page_content or "").strip(),
                    "score": float(score) if score is not None else None,
                    **metadata,
                }
            )

        enough_evidence = any(
            (item.get("score") is not None and item["score"] >= score_threshold)
            for item in results
        )

        fallback_message = None
        if not results:
            fallback_message = "관련 문서를 찾지 못했습니다."
        elif not enough_evidence:
            fallback_message = "관련 문서는 찾았지만 충분히 근거가 강하지 않습니다."

        return {
            "query": cleaned_query,
            "search_type": "similarity_with_scores",
            "retrieved_count": len(results),
            "enough_evidence": enough_evidence,
            "results": results,
            "fallback_message": fallback_message,
        }

    except Exception as first_error:
        print(f"[KNOWLEDGE SEARCH TOOL] scored search failed: {first_error}")

        try:
            # ------------------------------------------------------
            # 2차: 점수 없는 일반 검색 fallback
            # ------------------------------------------------------
            docs = _vectorstore.similarity_search(cleaned_query, k=top_k)

            results: list[RetrievedChunk] = []

            for doc in docs:
                metadata = _normalize_metadata(doc.metadata)

                results.append(
                    {
                        "content": (doc.page_content or "").strip(),
                        "score": None,
                        **metadata,
                    }
                )

            return {
                "query": cleaned_query,
                "search_type": "similarity",
                "retrieved_count": len(results),
                "enough_evidence": len(results) > 0,
                "results": results,
                "fallback_message": None if results else "관련 문서를 찾지 못했습니다.",
            }

        except Exception as second_error:
            print(f"[KNOWLEDGE SEARCH TOOL ERROR] {second_error}")
            return {
                "query": cleaned_query,
                "search_type": "error",
                "retrieved_count": 0,
                "enough_evidence": False,
                "results": [],
                "fallback_message": "죄송합니다. 현재 문서 검색 중 문제가 발생했습니다.",
            }


def _format_chunks_for_legacy_response(search_result: KnowledgeSearchResult) -> str:
    """
    기존 faq_tool 문자열 반환 형식과의 하위호환용 포맷터.
    """
    results = search_result.get("results", [])
    fallback_message = search_result.get("fallback_message")

    if not results:
        return fallback_message or "관련 문서를 찾지 못했습니다."

    formatted_blocks: list[str] = []

    for idx, item in enumerate(results[:2], start=1):
        source_info = []

        if item.get("file_name"):
            source_info.append(f"문서: {item['file_name']}")
        if item.get("page") is not None:
            source_info.append(f"페이지: {item['page']}")
        if item.get("chunk_index") is not None:
            source_info.append(f"청크: {item['chunk_index']}")
        if item.get("score") is not None:
            source_info.append(f"유사도: {item['score']:.3f}")

        source_line = " | ".join(source_info)
        content = item.get("content", "").strip()

        block = f"[근거 {idx}]"
        if source_line:
            block += f"\n{source_line}"
        block += f"\n{content}"

        formatted_blocks.append(block)

    return "\n\n".join(formatted_blocks)


def faq_tool(query: str) -> str:
    """
    하위호환용 래퍼 함수.

    기존 코드가 faq_tool(query) -> str 을 기대하더라도
    내부적으로는 knowledge_search_tool을 사용하도록 유지한다.
    """
    search_result = knowledge_search_tool(
        query=query,
        top_k=4,
        score_threshold=0.15,
    )
    return _format_chunks_for_legacy_response(search_result)