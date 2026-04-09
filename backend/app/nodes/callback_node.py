from __future__ import annotations

try:
    from ..state import CallFlowState, reset_callback_state
    from ..tools.callback_tool import callback_tool
except ImportError:  # local test fallback
    from state import CallFlowState, reset_callback_state
    from callback_tool import callback_tool


def run(state: CallFlowState) -> CallFlowState:
    """
    Callback Tool 실행 노드

    실행 조건
    - collected_name, collected_phone가 모두 있을 때
    - dialogue_manager가 next_action="run_callback" 으로 결정했을 때
    """
    name = (state.get("collected_name") or "").strip()
    phone = (state.get("collected_phone") or "").strip()

    result = callback_tool(name, phone)
    state["tool_result"] = result

    if result["success"]:
        reset_callback_state(state)
        state["next_action"] = "finish"
    else:
        state["active_flow"] = "callback"
        if not name:
            state["awaiting_field"] = "name"
            state["next_action"] = "ask_name"
        else:
            state["awaiting_field"] = "phone"
            state["next_action"] = "ask_phone"

    return state


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
