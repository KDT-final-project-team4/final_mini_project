from __future__ import annotations

try:
    from app.state import CallFlowState, reset_callback_state
    from app.tools.callback_tool import callback_tool
    from app.config import get_logger, settings
except ImportError:  # local test fallback
    from state import CallFlowState, reset_callback_state
    from tools.callback_tool import callback_tool
    from config import get_logger, settings


logger = get_logger(__name__)


def _state_summary(state: CallFlowState) -> dict:
    return {
        "session_id": state.get("session_id"),
        "intent": state.get("intent"),
        "next_action": state.get("next_action"),
        "active_flow": state.get("active_flow"),
        "awaiting_field": state.get("awaiting_field"),
        "collected_name": state.get("collected_name"),
        "collected_phone": state.get("collected_phone"),
    }


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
    logger.info(
        "callback_node.enter state=%s callback_mode=%s",
        _state_summary(state),
        settings.CALLBACK_MODE,
    )

    next_action = state.get("next_action")

    if next_action == "ask_name":
        state["final_response"] = _get_error_message(state) or "성함을 알려주세요."
        logger.info("callback_node.ask_name state=%s", _state_summary(state))
        return state

    if next_action == "ask_phone":
        state["final_response"] = _get_error_message(state) or "전화번호를 알려주세요. 예: 010-1234-5678"
        logger.info("callback_node.ask_phone state=%s", _state_summary(state))
        return state

    if next_action != "run_callback":
        logger.info("callback_node.skip next_action=%s state=%s", next_action, _state_summary(state))
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
        logger.warning("callback_node.missing_name state=%s", _state_summary(state))
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
        logger.warning("callback_node.missing_phone state=%s", _state_summary(state))
        return state

    if settings.CALLBACK_MODE != "mock":
        logger.warning("callback_node mode=%s not wired yet, fallback to callback_tool", settings.CALLBACK_MODE)

    result = callback_tool(name, phone)
    state["tool_result"] = result

    if result.get("success"):
        state["next_action"] = "finish"
        reset_callback_state(state)
        logger.info(
            "callback_node.success reset_done=True state=%s tool_result=%s",
            _state_summary(state),
            state.get("tool_result"),
        )
    else:
        state["active_flow"] = "callback"
        state["awaiting_field"] = "phone" if name else "name"
        state["next_action"] = "ask_phone" if name else "ask_name"
        logger.warning(
            "callback_node.failure state=%s tool_result=%s",
            _state_summary(state),
            state.get("tool_result"),
        )

    return state


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