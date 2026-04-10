from __future__ import annotations

from typing import Any, NotRequired, TypedDict


class RetrievedChunk(TypedDict, total=False):
    """
    knowledge_search_tool에서 반환되는 개별 검색 근거(chunk) 구조.
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
    retrieval 단계의 전체 검색 결과 구조.
    """

    query: str
    search_type: str
    retrieved_count: int
    enough_evidence: bool
    results: list[RetrievedChunk]
    fallback_message: str | None


class EvidenceResult(TypedDict, total=False):
    """
    evidence_check_node에서 생성하는 근거 판정 결과 구조.
    """

    query: str
    has_evidence: bool
    enough_evidence: bool
    needs_clarification: bool
    should_fallback: bool
    reason: str
    top_score: float | None
    needs_multi_chunk: bool
    selected_evidence: list[RetrievedChunk]
    evidence_summary: str


class GraphState(TypedDict, total=False):
    """
    LangGraph 전체에서 공유되는 상태.

    설계 원칙
    ----------
    1. 현재 미니 버전에서 실제 쓰는 필드
    2. 곧바로 붙일 retrieval / evidence / action 구조
    3. 이후 음성/멀티테넌시 확장 시 필요한 필드

    를 한 번에 수용할 수 있게 설계한다.

    주의
    ----
    아직 모든 필드가 실제 코드에서 즉시 사용되지는 않아도 괜찮다.
    중요한 것은 앞으로의 구조 변경 시 state 타입이 발목을 잡지 않도록
    미리 확장 가능한 형태로 잡아두는 것이다.
    """

    # --------------------------------------------------------------
    # 기본 입력 / 출력
    # --------------------------------------------------------------
    user_input: str
    final_response: str

    # --------------------------------------------------------------
    # 현재 대화 흐름 제어
    # --------------------------------------------------------------
    intent: str
    next_action: str
    active_flow: str

    # --------------------------------------------------------------
    # callback / slot filling 관련 상태
    # --------------------------------------------------------------
    collected_name: str
    collected_phone: str

    # 향후 slot filling 일반화를 위한 확장 필드
    slots: dict[str, Any]

    # --------------------------------------------------------------
    # retrieval / evidence 구조
    # --------------------------------------------------------------
    # retrieval 단계의 원본 검색 결과
    tool_result: KnowledgeSearchResult | dict[str, Any] | str

    # retrieval 결과를 사람이 확인하기 쉽게 요약한 preview
    retrieval_preview: str

    # evidence 점검 결과
    evidence_result: EvidenceResult | dict[str, Any]

    # --------------------------------------------------------------
    # action 결과
    # --------------------------------------------------------------
    # callback, note 저장, summary 저장 등
    action_result: dict[str, Any]

    # --------------------------------------------------------------
    # 세션 / 멀티테넌시 확장 대비
    # --------------------------------------------------------------
    session_id: str
    tenant_id: str

    # --------------------------------------------------------------
    # guardrail / 정책 플래그 확장 대비
    # --------------------------------------------------------------
    guardrail_flags: dict[str, Any]

    # --------------------------------------------------------------
    # 디버깅 / 로깅 / 향후 메시지 기반 확장 대비
    # --------------------------------------------------------------
    messages: list[Any]
    debug_info: dict[str, Any]

    # --------------------------------------------------------------
    # 하위 호환용 선택 필드
    # --------------------------------------------------------------
    question: NotRequired[str]
    message: NotRequired[str]
    last_user_message: NotRequired[str]