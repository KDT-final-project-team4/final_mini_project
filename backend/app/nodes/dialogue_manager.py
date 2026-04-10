from __future__ import annotations

import re

try:
    from app.state import CallFlowState
except ImportError:  # local test fallback
    from state import CallFlowState


_PHONE_PATTERN = re.compile(r"^[0-9\-\s]+$")
_NAME_PATTERN = re.compile(r"^[A-Za-z가-힣\s]{2,20}$")

FAQ_KEYWORDS = (
    "운영시간",
    "영업시간",
    "운영 시간",
    "영업 시간",
    "몇 시",
    "오픈",
    "마감",
)

VISION_KEYWORDS = (
    "사진",
    "이미지",
    "첨부",
    "이거 이상",
    "문제",
    "오류",
    "고장",
    "봐줘",
    "확인해줘",
)

CALLBACK_KEYWORDS = (
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

NAME_BLOCK_KEYWORDS = (
    "알려줘",
    "해줘",
    "부탁",
    "문의",
    "이상",
    "문제",
    "오류",
    "사진",
    "이미지",
    "운영",
    "영업",
)


def _clean_text(text: str | None) -> str:
    return (text or "").strip()


def _contains_keyword(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def _looks_like_phone(text: str) -> bool:
    clean = _clean_text(text)
    digits = re.sub(r"[^0-9]", "", clean)
    return bool(clean) and bool(_PHONE_PATTERN.match(clean)) and len(digits) in (10, 11)


def _looks_like_name(text: str) -> bool:
    clean = _clean_text(text)

    if not clean:
        return False

    if _looks_like_phone(clean):
        return False

    lowered = clean.lower()
    if _contains_keyword(clean, FAQ_KEYWORDS):
        return False
    if _contains_keyword(clean, VISION_KEYWORDS):
        return False
    if _contains_keyword(lowered, CALLBACK_KEYWORDS):
        return False
    if _contains_keyword(clean, NAME_BLOCK_KEYWORDS):
        return False

    return bool(_NAME_PATTERN.fullmatch(clean))


def _set_callback_validation(
    state: CallFlowState,
    *,
    field: str,
    error: str,
    user_input: str,
) -> CallFlowState:
    state["tool_result"] = {
        "success": False,
        "tool_name": "callback_validation",
        "message": "콜백 입력값 확인 필요",
        "data": {
            "field": field,
            "user_input": user_input,
        },
        "error": error,
    }
    return state


def _start_callback_flow(state: CallFlowState) -> CallFlowState:
    state["active_flow"] = "callback"
    state["awaiting_field"] = "name"
    state["next_action"] = "ask_name"
    return state


def _handle_callback_flow(state: CallFlowState) -> CallFlowState:
    user_input = _clean_text(state.get("user_input"))
    awaiting_field = state.get("awaiting_field")

    if awaiting_field == "name":
        if not user_input:
            state["next_action"] = "ask_name"
            return _set_callback_validation(
                state,
                field="name",
                error="성함이 입력되지 않았습니다.",
                user_input=user_input,
            )

        if not _looks_like_name(user_input):
            state["next_action"] = "ask_name"
            return _set_callback_validation(
                state,
                field="name",
                error="성함만 입력해주세요. 예: 홍길동",
                user_input=user_input,
            )

        state["collected_name"] = user_input
        state["awaiting_field"] = "phone"
        state["next_action"] = "ask_phone"
        state["tool_result"] = None
        return state

    if awaiting_field == "phone":
        if not _looks_like_phone(user_input):
            state["next_action"] = "ask_phone"
            return _set_callback_validation(
                state,
                field="phone",
                error="전화번호 형식이 올바르지 않습니다. 예: 010-1234-5678",
                user_input=user_input,
            )

        state["collected_phone"] = user_input
        state["next_action"] = "run_callback"
        state["tool_result"] = None
        return state

    if not state.get("collected_name"):
        state["awaiting_field"] = "name"
        state["next_action"] = "ask_name"
        return state

    if not state.get("collected_phone"):
        state["awaiting_field"] = "phone"
        state["next_action"] = "ask_phone"
        return state

    state["next_action"] = "run_callback"
    return state


def run(state: CallFlowState) -> CallFlowState:
    """
    Dialogue Manager Node

    역할
    - state를 보고 다음 액션(next_action)을 결정한다.
    - active_flow가 있으면 현재 흐름을 우선 처리한다.

    next_action 규칙
    - faq -> run_faq
    - callback 시작 -> ask_name
    - callback 이름 수집 완료 -> ask_phone
    - callback 이름/전화번호 수집 완료 -> run_callback
    - vision -> run_vision
    - unknown -> run_vision
    """
    state["tool_result"] = None
    state["final_response"] = None

    if state.get("active_flow") == "callback":
        return _handle_callback_flow(state)

    intent = state.get("intent")

    if intent == "faq":
        state["next_action"] = "run_faq"
        return state

    if intent == "callback":
        return _start_callback_flow(state)

    if intent == "vision":
        state["next_action"] = "run_vision"
        return state

    state["next_action"] = "run_vision"
    return state


# graph.py 호환용 별칭
dialogue_manager = run


if __name__ == "__main__":
    examples = [
        {
            "session_id": "demo-1",
            "user_input": "운영시간 알려줘",
            "intent": "faq",
            "next_action": None,
            "active_flow": None,
            "awaiting_field": None,
            "collected_name": None,
            "collected_phone": None,
            "tool_result": None,
            "final_response": None,
        },
        {
            "session_id": "demo-2",
            "user_input": "상담원 연결해줘",
            "intent": "callback",
            "next_action": None,
            "active_flow": None,
            "awaiting_field": None,
            "collected_name": None,
            "collected_phone": None,
            "tool_result": None,
            "final_response": None,
        },
        {
            "session_id": "demo-2",
            "user_input": "홍길동",
            "intent": "callback",
            "next_action": None,
            "active_flow": "callback",
            "awaiting_field": "name",
            "collected_name": None,
            "collected_phone": None,
            "tool_result": None,
            "final_response": None,
        },
        {
            "session_id": "demo-2",
            "user_input": "010-1234-5678",
            "intent": "callback",
            "next_action": None,
            "active_flow": "callback",
            "awaiting_field": "phone",
            "collected_name": "홍길동",
            "collected_phone": None,
            "tool_result": None,
            "final_response": None,
        },
    ]

    for example in examples:
        print(run(example))