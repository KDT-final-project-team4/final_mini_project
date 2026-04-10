from __future__ import annotations

try:
    from app.state import CallFlowState, reset_callback_state
    from app.tools.callback_tool import callback_tool
except ImportError:  # local test fallback
    from state import CallFlowState, reset_callback_state
    from tools.callback_tool import callback_tool


def _get_error_message(state: CallFlowState) -> str | None:
    tool_result = state.get("tool_result") or {}
    error = tool_result.get("error")
    if isinstance(error, str) and error.strip():
        return error
    return None


def run(state: CallFlowState) -> CallFlowState:
    """
    Callback Node

    역할
    - ask_name / ask_phone 인 경우 사용자에게 보여줄 문구를 만든다.
    - run_callback 인 경우 callback_tool을 실행한다.
    """
    next_action = state.get("next_action")

    if next_action == "ask_name":
        state["final_response"] = _get_error_message(state) or "성함을 알려주세요."
        return state

    if next_action == "ask_phone":
        state["final_response"] = _get_error_message(state) or "전화번호를 알려주세요. 예: 010-1234-5678"
        return state

    if next_action != "run_callback":
        return state

    name = (state.get("collected_name") or "").strip()
    phone = (state.get("collected_phone") or "").strip()

    if not name:
        state["active_flow"] = "callback"
        state["awaiting_field"] = "name"
        state["next_action"] = "ask_name"
        state["tool_result"] = {
            "success": False,
            "tool_name": "callback_validation",
            "message": "콜백 입력값 확인 필요",
            "data": {"field": "name", "user_input": ""},
            "error": "성함을 먼저 입력해주세요.",
        }
        state["final_response"] = "성함을 먼저 입력해주세요."
        return state

    if not phone:
        state["active_flow"] = "callback"
        state["awaiting_field"] = "phone"
        state["next_action"] = "ask_phone"
        state["tool_result"] = {
            "success": False,
            "tool_name": "callback_validation",
            "message": "콜백 입력값 확인 필요",
            "data": {"field": "phone", "user_input": ""},
            "error": "전화번호를 먼저 입력해주세요.",
        }
        state["final_response"] = "전화번호를 먼저 입력해주세요."
        return state

    result = callback_tool(name, phone)
    state["tool_result"] = result

    if result.get("success"):
        state["next_action"] = "finish"
        reset_callback_state(state)
    else:
        state["active_flow"] = "callback"
        if not name:
            state["awaiting_field"] = "name"
            state["next_action"] = "ask_name"
        else:
            state["awaiting_field"] = "phone"
            state["next_action"] = "ask_phone"

    return state


# graph.py 호환용 별칭
callback_node = run


if __name__ == "__main__":
    mock_state: CallFlowState = {
        "session_id": "test-session",
        "user_input": "010-1234-5678",
        "intent": "callback",
        "next_action": "run_callback",
        "active_flow": "callback",
        "awaiting_field": "phone",
        "collected_name": "홍길동",
        "collected_phone": "010-1234-5678",
        "tool_result": None,
        "final_response": None,
    }
    print(run(mock_state))