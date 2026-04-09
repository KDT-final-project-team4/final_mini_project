from __future__ import annotations

from typing import Final

try:
    from app.state import CallFlowState
except ImportError:  # local test fallback
    from state import CallFlowState


FAQ_KEYWORDS: Final[tuple[str, ...]] = (
    "운영시간",
    "영업시간",
    "운영 시간",
    "영업 시간",
    "몇 시",
    "오픈",
    "마감",
)

CALLBACK_KEYWORDS: Final[tuple[str, ...]] = (
    "상담원",
    "상담",
    "전화",
    "콜백",
    "callback",
    "연결",
    "통화",
    "연락",
    "전화 부탁",
    "전화 주세요",
    "전화좀",
)


def _normalize_text(text: str) -> str:
    return text.strip().lower()


def _contains_keyword(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def _is_callback_in_progress(state: CallFlowState) -> bool:
    return (
        state.get("active_flow") == "callback"
        or state.get("awaiting_field") in ("name", "phone")
    )


def classify_intent(user_input: str) -> str:
    """
    rule-based intent 분류

    우선순위
    1. callback
    2. faq
    3. unknown
    """
    text = _normalize_text(user_input)

    if not text:
        return "unknown"

    if _contains_keyword(text, CALLBACK_KEYWORDS):
        return "callback"

    if _contains_keyword(text, FAQ_KEYWORDS):
        return "faq"

    return "unknown"


def run(state: CallFlowState) -> CallFlowState:
    """
    Intent Router Node

    역할
    - 현재 사용자 입력을 faq / callback / unknown 중 하나로 분류
    - 단, callback 진행 중이면 intent를 callback으로 유지
    """
    if _is_callback_in_progress(state):
        state["intent"] = "callback"
        return state

    user_input = state.get("user_input", "")
    state["intent"] = classify_intent(user_input)
    return state


if __name__ == "__main__":
    examples = [
        "운영시간 알려줘",
        "상담원 연결해줘",
        "전화 부탁해요",
        "이거 이상해요",
        "사진 봐주세요",
    ]

    for text in examples:
        mock_state: CallFlowState = {
            "session_id": "test-session",
            "user_input": text,
            "intent": None,
            "next_action": None,
            "active_flow": None,
            "awaiting_field": None,
            "collected_name": None,
            "collected_phone": None,
            "tool_result": None,
            "final_response": None,
        }
        print(text, "->", run(mock_state)["intent"])
