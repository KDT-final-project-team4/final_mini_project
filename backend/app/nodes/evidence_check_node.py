from __future__ import annotations

from typing import Any


def evidence_check_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    Retrieval 결과를 바탕으로 근거 충분성을 점검하는 노드.

    이 노드의 책임
    --------------
    1. retrieval 결과가 실제로 존재하는지 확인
    2. 상위 chunk들의 score를 바탕으로 근거가 충분한지 판단
    3. 여러 chunk를 함께 봐야 하는 질문인지 간단히 판단
    4. response_node가 쉽게 사용할 수 있도록 evidence_result를 state에 저장

    이 노드는 '최종 응답 생성'을 하지 않는다.
    오직 근거 점검만 수행한다.
    """

    tool_result = state.get("tool_result") or {}
    query = (tool_result.get("query") or state.get("user_input") or "").strip()
    results = tool_result.get("results") or []

    # --------------------------------------------------------------
    # 1. 검색 결과가 아예 없는 경우
    # --------------------------------------------------------------
    if not results:
        evidence_result = {
            "query": query,
            "has_evidence": False,
            "enough_evidence": False,
            "needs_clarification": False,
            "should_fallback": True,
            "reason": "no_results",
            "selected_evidence": [],
            "evidence_summary": "관련 문서를 찾지 못했습니다.",
        }

        return {
            **state,
            "evidence_result": evidence_result,
        }

    # --------------------------------------------------------------
    # 2. score 분석
    # --------------------------------------------------------------
    # 주의:
    # similarity_search_with_relevance_scores를 썼을 때만 점수가 있을 수 있다.
    # fallback similarity_search 결과라면 score가 None일 수 있다.
    scored_results = [item for item in results if item.get("score") is not None]
    top_score = scored_results[0]["score"] if scored_results else None

    # 상위 2개 근거만 우선 사용
    selected_evidence = results[:2]

    # --------------------------------------------------------------
    # 3. 질문 유형에 따른 간단한 휴리스틱
    # --------------------------------------------------------------
    # 절차형 / 복합 질문은 여러 chunk가 필요할 가능성이 높다.
    lowered_query = query.lower()

    multi_chunk_keywords = [
        "같이",
        "그리고",
        "순서",
        "절차",
        "어떻게 처리",
        "환불",
        "교환",
        "반품",
        "취소",
        "예외",
        "조건",
    ]

    needs_multi_chunk = any(keyword in query for keyword in multi_chunk_keywords) or any(
        keyword in lowered_query for keyword in multi_chunk_keywords
    )

    # --------------------------------------------------------------
    # 4. 근거 충분성 판단
    # --------------------------------------------------------------
    # 기준은 너무 빡세게 잡지 않는다.
    # 지금 단계에서는 response 전에 1차 안전장치만 두는 목적이다.
    if top_score is None:
        # score가 없는 fallback retrieval이면
        # 결과가 있다는 사실만으로 약한 근거가 있다고 본다.
        enough_evidence = len(results) > 0
        reason = "no_score_results"
    else:
        if top_score >= 0.35:
            enough_evidence = True
            reason = "strong_match"
        elif top_score >= 0.18:
            enough_evidence = True
            reason = "moderate_match"
        else:
            enough_evidence = False
            reason = "weak_match"

    # --------------------------------------------------------------
    # 5. clarification 필요 여부
    # --------------------------------------------------------------
    # 복합 질문인데 근거가 약하면, 바로 단정 답변보다
    # 추가 설명/질문 유도 쪽이 더 안전하다.
    needs_clarification = needs_multi_chunk and not enough_evidence

    # --------------------------------------------------------------
    # 6. fallback 여부 결정
    # --------------------------------------------------------------
    should_fallback = not enough_evidence and not needs_clarification

    # --------------------------------------------------------------
    # 7. evidence summary 생성
    # --------------------------------------------------------------
    summary_blocks: list[str] = []

    for idx, item in enumerate(selected_evidence, start=1):
        parts = []

        if item.get("file_name"):
            parts.append(f"문서: {item['file_name']}")
        if item.get("page") is not None:
            parts.append(f"페이지: {item['page']}")
        if item.get("chunk_index") is not None:
            parts.append(f"청크: {item['chunk_index']}")
        if item.get("score") is not None:
            parts.append(f"유사도: {item['score']:.3f}")

        header = " | ".join(parts)
        content = (item.get("content") or "").strip()
        short_content = content[:300] + ("..." if len(content) > 300 else "")

        block = f"[근거 {idx}]"
        if header:
            block += f"\n{header}"
        block += f"\n{short_content}"

        summary_blocks.append(block)

    evidence_summary = "\n\n".join(summary_blocks)

    evidence_result = {
        "query": query,
        "has_evidence": True,
        "enough_evidence": enough_evidence,
        "needs_clarification": needs_clarification,
        "should_fallback": should_fallback,
        "reason": reason,
        "top_score": top_score,
        "needs_multi_chunk": needs_multi_chunk,
        "selected_evidence": selected_evidence,
        "evidence_summary": evidence_summary,
    }

    print("\n[EVIDENCE CHECK]")
    print("top_score:", evidence_result.get("top_score"))
    print("enough_evidence:", evidence_result.get("enough_evidence"))
    print("should_fallback:", evidence_result.get("should_fallback"))

    return {
        **state,
        "evidence_result": evidence_result,
    }