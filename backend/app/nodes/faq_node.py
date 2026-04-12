from __future__ import annotations

try:
    from app.state import CallFlowState
    from app.tools.faq_tool import faq_tool
    from app.config import get_logger, settings
except ImportError:  # local test fallback
    from state import CallFlowState
    from tools.faq_tool import faq_tool
    from config import get_logger, settings


logger = get_logger(__name__)


def _state_summary(state: CallFlowState) -> dict:
    return {
        "session_id": state.get("session_id"),
        "user_input": state.get("user_input"),
        "intent": state.get("intent"),
        "next_action": state.get("next_action"),
    }


def run(state: CallFlowState) -> CallFlowState:
    """
    FAQ 실행 노드

    역할
    - 현재 user_input을 faq_tool에 전달한다.
    - 실행 결과를 state['tool_result']에 저장한다.
    """
    logger.info("faq_node.enter state=%s faq_mode=%s", _state_summary(state), settings.FAQ_MODE)

    query = (state.get("user_input") or "").strip()

    # 현재는 faq_tool만 구현되어 있으므로 mode는 로그/토글만 우선 반영
    if settings.FAQ_MODE in {"llm", "rag"}:
        logger.warning("faq_node mode=%s not wired yet, fallback to faq_tool", settings.FAQ_MODE)

    state["tool_result"] = faq_tool(query)

    logger.info(
        "faq_node.exit success=%s tool_name=%s state=%s",
        (state.get("tool_result") or {}).get("success"),
        (state.get("tool_result") or {}).get("tool_name"),
        _state_summary(state),
    )
    return state


faq_node = run


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