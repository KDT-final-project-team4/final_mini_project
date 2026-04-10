from __future__ import annotations

try:
    from app.state import CallFlowState
except ImportError:  # local test fallback
    from state import CallFlowState


ASK_NAME_MESSAGE = "상담 접수를 도와드릴게요. 먼저 성함을 알려주세요."
ASK_NAME_RETRY_MESSAGE = "성함만 다시 입력해주세요. 예: 홍길동"
ASK_PHONE_MESSAGE = "확인 감사합니다. 연락받으실 전화번호를 입력해주세요."
ASK_PHONE_RETRY_MESSAGE = "전화번호 형식을 다시 확인해주세요. 예: 010-1234-5678"
CALLBACK_CANCEL_MESSAGE = "콜백 요청을 취소했어요. 다른 도움이 필요하시면 말씀해주세요."
VISION_FALLBACK_MESSAGE = "정확한 확인을 위해 사진을 보내주세요."
UNKNOWN_FALLBACK_MESSAGE = "도움을 위해 조금 더 자세히 말씀해주시거나 사진을 보내주세요."


def _build_tool_response(state: CallFlowState) -> str:
    tool_result = state.get("tool_result")
    if not tool_result:
        return UNKNOWN_FALLBACK_MESSAGE

    tool_name = tool_result.get("tool_name")
    data = tool_result.get("data") or {}

    if tool_name == "faq":
        return data.get("answer", UNKNOWN_FALLBACK_MESSAGE)

    if tool_name == "vision":
        return data.get("guide", VISION_FALLBACK_MESSAGE)

    if tool_name == "callback":
        if tool_result.get("success"):
            name = data.get("name", "고객님")
            masked_phone = data.get("masked_phone", "비공개")
            return f"{name}님, 콜백 등록이 완료됐어요. {masked_phone} 번호로 연락드릴게요."

        error = tool_result.get("error") or "입력값을 다시 확인해주세요."
        return f"콜백 등록에 실패했어요. {error}"

    if tool_name == "callback_validation":
        field = data.get("field")
        if field == "name":
            return ASK_NAME_RETRY_MESSAGE
        if field == "phone":
            return ASK_PHONE_RETRY_MESSAGE
        return tool_result.get("error") or UNKNOWN_FALLBACK_MESSAGE

    return UNKNOWN_FALLBACK_MESSAGE


def run(state: CallFlowState) -> CallFlowState:
    """
    Response Node

    역할
    - next_action 또는 tool_result를 기준으로 최종 사용자 응답 생성
    - 사용자에게 보여줄 문장을 final_response에 저장
    """
    if state.get("final_response"):
        return state

    next_action = state.get("next_action")
    tool_result = state.get("tool_result")

    if next_action == "ask_name":
        if tool_result and tool_result.get("tool_name") == "callback_validation":
            state["final_response"] = _build_tool_response(state)
        else:
            state["final_response"] = ASK_NAME_MESSAGE
        return state

    if next_action == "ask_phone":
        if tool_result and tool_result.get("tool_name") == "callback_validation":
            state["final_response"] = _build_tool_response(state)
        else:
            state["final_response"] = ASK_PHONE_MESSAGE
        return state

    if next_action == "finish" and state.get("tool_result") is None:
        state["final_response"] = CALLBACK_CANCEL_MESSAGE
        return state

    state["final_response"] = _build_tool_response(state)
    return state


# graph.py 호환용 별칭
response_node = run


if __name__ == "__main__":
    examples = [
        {
            "session_id": "r1",
            "user_input": "",
            "intent": "callback",
            "next_action": "ask_name",
            "active_flow": "callback",
            "awaiting_field": "name",
            "collected_name": None,
            "collected_phone": None,
            "tool_result": None,
            "final_response": None,
        },
        {
            "session_id": "r2",
            "user_input": "운영시간 알려줘",
            "intent": "callback",
            "next_action": "ask_name",
            "active_flow": "callback",
            "awaiting_field": "name",
            "collected_name": None,
            "collected_phone": None,
            "tool_result": {
                "success": False,
                "tool_name": "callback_validation",
                "message": "콜백 입력값 확인 필요",
                "data": {"field": "name", "user_input": "운영시간 알려줘"},
                "error": "성함만 입력해주세요. 예: 홍길동",
            },
            "final_response": None,
        },
        {
            "session_id": "r3",
            "user_input": "010123",
            "intent": "callback",
            "next_action": "ask_phone",
            "active_flow": "callback",
            "awaiting_field": "phone",
            "collected_name": "홍길동",
            "collected_phone": None,
            "tool_result": {
                "success": False,
                "tool_name": "callback_validation",
                "message": "콜백 입력값 확인 필요",
                "data": {"field": "phone", "user_input": "010123"},
                "error": "전화번호 형식이 올바르지 않습니다. 예: 010-1234-5678",
            },
            "final_response": None,
        },
        {
            "session_id": "r4",
            "user_input": "",
            "intent": "callback",
            "next_action": "finish",
            "active_flow": None,
            "awaiting_field": None,
            "collected_name": None,
            "collected_phone": None,
            "tool_result": {
                "success": True,
                "tool_name": "callback",
                "message": "콜백 등록 성공",
                "data": {
                    "status": "registered",
                    "name": "홍길동",
                    "phone": "01012345678",
                    "masked_phone": "010-****-5678",
                },
                "error": None,
            },
            "final_response": None,
        },
    ]

    for example in examples:
        print(run(example))