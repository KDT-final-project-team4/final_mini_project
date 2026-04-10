from __future__ import annotations

from typing import Any

from app.tools.faq_tool import knowledge_search_tool


def faq_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    FAQ specialist node를 retrieval 중심 노드로 확장한 버전.

    현재 역할
    --------
    1. 사용자 질문을 state에서 읽는다.
    2. knowledge_search_tool()로 관련 문서 chunk를 검색한다.
    3. 검색 결과를 tool_result에 구조화된 형태로 저장한다.
    4. 기존 구조와의 호환 및 디버깅을 위해 retrieval_preview를 함께 저장한다.

    왜 이렇게 바꾸는가?
    -------------------
    이전에는 faq_node가 사실상:
        질문 -> 검색 -> 문자열 근거
    수준이었다.

    하지만 이제는:
        Retrieval
        -> Evidence Check
        -> Response

    구조로 가고 있으므로, faq_node는 "검색 결과 적재 노드"가 되어야 한다.
    """

    # --------------------------------------------------------------
    # 1. 사용자 질문 추출
    # --------------------------------------------------------------
    # 현재 프로젝트에서 user_input을 주로 쓰지만,
    # 하위호환을 위해 question / message / last_user_message도 함께 확인
    query = (
        state.get("user_input")
        or state.get("question")
        or state.get("last_user_message")
        or state.get("message")
        or ""
    ).strip()

    # 질문이 비어 있으면 빈 검색 결과를 반환
    if not query:
        empty_result = {
            "query": "",
            "search_type": "empty",
            "retrieved_count": 0,
            "enough_evidence": False,
            "results": [],
            "fallback_message": "검색할 질문이 없습니다.",
        }

        return {
            **state,
            "tool_result": empty_result,
            "retrieval_preview": "검색할 질문이 없습니다.",
        }

    # --------------------------------------------------------------
    # 2. 구조화된 retrieval 실행
    # --------------------------------------------------------------
    search_result = knowledge_search_tool(
        query=query,
        top_k=4,
        score_threshold=0.15,
    )

    # --------------------------------------------------------------
    # 3. 사람이 보기 쉬운 preview 생성
    # --------------------------------------------------------------
    retrieval_preview = _build_retrieval_preview(search_result)

    print("\n[FAQ NODE]")
    print("query:", query)
    print("retrieved_count:", search_result.get("retrieved_count"))
    print("preview:", retrieval_preview[:300])

    # --------------------------------------------------------------
    # 4. state 반영
    # --------------------------------------------------------------
    # tool_result:
    #   evidence_check_node와 response_node가 사용할 정식 retrieval 결과
    #
    # retrieval_preview:
    #   디버깅 / 하위호환 / 로그 확인용 문자열 요약
    return {
        **state,
        "tool_result": search_result,
        "retrieval_preview": retrieval_preview,
    }


def _build_retrieval_preview(search_result: dict[str, Any]) -> str:
    """
    검색 결과를 사람이 빠르게 확인할 수 있는 문자열로 요약한다.

    목적
    ----
    - 개발 중 디버깅 편의
    - 검색 결과를 로그에서 빠르게 확인
    - 기존 문자열 중심 구조와의 하위호환 보조

    주의
    ----
    이 preview는 최종 응답이 아니다.
    최종 응답은 response_node가 evidence_result를 바탕으로 만든다.
    """
    results = search_result.get("results", [])
    fallback_message = search_result.get("fallback_message")

    if not results:
        return fallback_message or "관련 문서를 찾지 못했습니다."

    blocks: list[str] = []

    # preview는 너무 길면 보기 어려우므로 상위 2개만 사용
    for idx, item in enumerate(results[:2], start=1):
        source_parts = []

        if item.get("file_name"):
            source_parts.append(f"문서: {item['file_name']}")
        if item.get("page") is not None:
            source_parts.append(f"페이지: {item['page']}")
        if item.get("chunk_index") is not None:
            source_parts.append(f"청크: {item['chunk_index']}")
        if item.get("score") is not None:
            source_parts.append(f"유사도: {item['score']:.3f}")

        source_line = " | ".join(source_parts)
        content = (item.get("content") or "").strip()

        short_content = content[:400]
        if len(content) > 400:
            short_content += "..."

        block = f"[검색근거 {idx}]"
        if source_line:
            block += f"\n{source_line}"
        block += f"\n{short_content}"

        blocks.append(block)

    return "\n\n".join(blocks)