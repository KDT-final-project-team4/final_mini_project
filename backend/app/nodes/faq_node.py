from __future__ import annotations

try:
    from app.state import CallFlowState
    from app.tools.faq_tool import faq_tool
except ImportError:  # local test fallback
    from state import CallFlowState
    from faq_tool import faq_tool


def run(state: CallFlowState) -> CallFlowState:
    """
    FAQ 실행 노드

    역할
    - 현재 user_input을 faq_tool에 전달한다.
    - 실행 결과를 state['tool_result']에 저장한다.
    """
    query = (state.get("user_input") or "").strip()
    state["tool_result"] = faq_tool(query)
    return state


if __name__ == "__main__":
    mock_state: CallFlowState = {
        "session_id": "faq-test",
        "user_input": "운영시간 알려줘",
        "intent": "faq",
        "next_action": "run_faq",
        "active_flow": None,
        "awaiting_field": None,
        "collected_name": None,
        "collected_phone": None,
        "tool_result": None,
        "final_response": None,
    }
    print(run(mock_state))
