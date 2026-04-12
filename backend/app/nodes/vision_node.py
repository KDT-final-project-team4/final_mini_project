from __future__ import annotations

try:
    from app.state import CallFlowState
    from app.tools.vision_tool import vision_tool
    from app.config import get_logger, settings
except ImportError:  # local test fallback
    from state import CallFlowState
    from tools.vision_tool import vision_tool
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
    Vision 실행 노드

    역할
    - vision_tool을 실행한다.
    - 실행 결과를 state['tool_result']에 저장한다.
    """
    logger.info("vision_node.enter state=%s vision_mode=%s", _state_summary(state), settings.VISION_MODE)

    if settings.VISION_MODE != "mock":
        logger.warning("vision_node mode=%s not wired yet, fallback to vision_tool", settings.VISION_MODE)

    state["tool_result"] = vision_tool()

    logger.info(
        "vision_node.exit success=%s tool_name=%s state=%s",
        (state.get("tool_result") or {}).get("success"),
        (state.get("tool_result") or {}).get("tool_name"),
        _state_summary(state),
    )
    return state


vision_node = run


if __name__ == "__main__":
    mock_state: CallFlowState = {
        "session_id": "vision-test",
        "user_input": "이거 이상해요",
        "intent": "vision",
        "next_action": "run_vision",
        "active_flow": None,
        "awaiting_field": None,
        "collected_name": None,
        "collected_phone": None,
        "tool_result": None,
        "final_response": None,
    }
    print(run(mock_state))