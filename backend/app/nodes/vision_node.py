from __future__ import annotations

try:
    from app.state import CallFlowState
    from app.tools.vision_tool import vision_tool
except ImportError:  # local test fallback
    from state import CallFlowState
    from vision_tool import vision_tool


def run(state: CallFlowState) -> CallFlowState:
    """
    Vision 실행 노드

    역할
    - vision_tool을 실행한다.
    - 실행 결과를 state['tool_result']에 저장한다.
    """
    state["tool_result"] = vision_tool()
    return state


if __name__ == "__main__":
    mock_state: CallFlowState = {
        "session_id": "vision-test",
        "user_input": "이거 이상해요",
        "intent": "unknown",
        "next_action": "run_vision",
        "active_flow": None,
        "awaiting_field": None,
        "collected_name": None,
        "collected_phone": None,
        "tool_result": None,
        "final_response": None,
    }
    print(run(mock_state))
