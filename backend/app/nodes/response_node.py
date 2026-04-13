from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openai import OpenAI as OpenAIClient
else:
    OpenAIClient = Any

try:
    from openai import OpenAI as OpenAIClass
except ImportError:  # pragma: no cover
    OpenAIClass = None  # type: ignore

try:
    from app.state import CallFlowState
    from app.config import get_logger
    from app.prompts.response_prompt import (
        RESPONSE_SYSTEM_PROMPT,
        build_response_user_prompt,
    )
except ImportError:  # local test fallback
    from state import CallFlowState
    from config import get_logger
    from prompts.response_prompt import (
        RESPONSE_SYSTEM_PROMPT,
        build_response_user_prompt,
    )


logger = get_logger(__name__)

ASK_NAME_MESSAGE = "상담 접수를 도와드릴게요. 먼저 성함을 알려주세요."
ASK_NAME_RETRY_MESSAGE = "성함만 다시 입력해주세요. 예: 홍길동"
ASK_PHONE_MESSAGE = "확인 감사합니다. 연락받으실 전화번호를 입력해주세요."
ASK_PHONE_RETRY_MESSAGE = "전화번호 형식을 다시 확인해주세요. 예: 010-1234-5678"
CALLBACK_CANCEL_MESSAGE = "콜백 요청을 취소했어요. 다른 도움이 필요하시면 말씀해주세요."
VISION_FALLBACK_MESSAGE = "정확한 확인을 위해 사진을 보내주세요."
UNKNOWN_FALLBACK_MESSAGE = "도움을 위해 조금 더 자세히 말씀해주시거나 사진을 보내주세요."


def _state_summary(state: CallFlowState) -> dict:
    return {
        "session_id": state.get("session_id"),
        "intent": state.get("intent"),
        "next_action": state.get("next_action"),
        "active_flow": state.get("active_flow"),
        "awaiting_field": state.get("awaiting_field"),
        "collected_name": state.get("collected_name"),
        "collected_phone": state.get("collected_phone"),
        "final_response": state.get("final_response"),
    }


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


def _should_use_response_llm(state: CallFlowState) -> bool:
    if os.getenv("ENABLE_RESPONSE_LLM", "false").lower() != "true":
        return False

    if state.get("final_response"):
        return False

    next_action = state.get("next_action")
    if next_action in {"ask_name", "ask_phone"}:
        return False

    tool_result = state.get("tool_result") or {}
    if tool_result.get("tool_name") == "callback_validation":
        return False

    return True


def _get_openai_client() -> OpenAIClient | None:
    if OpenAIClass is None:
        logger.warning("response_node.openai_sdk_missing fallback_to_rule_based=True")
        return None

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        logger.warning("response_node.api_key_missing fallback_to_rule_based=True")
        return None

    return OpenAIClass(api_key=api_key)


def _get_response_model_name() -> str | None:
    model = os.getenv("OPENAI_RESPONSE_MODEL", "").strip()
    if not model:
        logger.warning("response_node.model_missing OPENAI_RESPONSE_MODEL is empty")
        return None
    return model


def _build_llm_response(state: CallFlowState) -> str | None:
    client = _get_openai_client()
    model = _get_response_model_name()

    if client is None or model is None:
        return None

    user_prompt = build_response_user_prompt(
        user_message=state.get("user_input", "") or "",
        intent=state.get("intent", "unknown") or "unknown",
        awaiting_field=state.get("awaiting_field"),
        tool_output=state.get("tool_result"),
    )

    try:
        response = client.responses.create(
            model=model,
            store=False,
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": RESPONSE_SYSTEM_PROMPT,
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": user_prompt,
                        }
                    ],
                },
            ],
        )

        text = (response.output_text or "").strip()
        if not text:
            logger.warning("response_node.llm_empty_output")
            return None

        return text

    except Exception as exc:
        logger.exception("response_node.llm_exception error=%s", exc)
        return None


def run(state: CallFlowState) -> CallFlowState:
    logger.info("response_node.enter state=%s", _state_summary(state))

    if state.get("final_response"):
        logger.info(
            "response_node.keep_existing final_response=%s",
            state.get("final_response"),
        )
        return state

    next_action = state.get("next_action")
    tool_result = state.get("tool_result")

    if next_action == "ask_name":
        if tool_result and tool_result.get("tool_name") == "callback_validation":
            state["final_response"] = _build_tool_response(state)
        else:
            state["final_response"] = ASK_NAME_MESSAGE
        logger.info("response_node.ask_name final_response=%s", state.get("final_response"))
        return state

    if next_action == "ask_phone":
        if tool_result and tool_result.get("tool_name") == "callback_validation":
            state["final_response"] = _build_tool_response(state)
        else:
            state["final_response"] = ASK_PHONE_MESSAGE
        logger.info("response_node.ask_phone final_response=%s", state.get("final_response"))
        return state

    if next_action == "finish" and state.get("tool_result") is None:
        state["final_response"] = CALLBACK_CANCEL_MESSAGE
        logger.info(
            "response_node.finish_without_tool final_response=%s",
            state.get("final_response"),
        )
        return state

    if _should_use_response_llm(state):
        llm_text = _build_llm_response(state)
        if llm_text:
            state["final_response"] = llm_text
            logger.info("response_node.llm_success final_response=%s", state.get("final_response"))
            return state

    state["final_response"] = _build_tool_response(state)
    logger.info("response_node.exit final_response=%s", state.get("final_response"))
    return state


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
            "intent": "faq",
            "next_action": "finish",
            "active_flow": None,
            "awaiting_field": None,
            "collected_name": None,
            "collected_phone": None,
            "tool_result": {
                "success": True,
                "tool_name": "faq",
                "message": "FAQ 조회 성공",
                "data": {"answer": "운영시간은 오전 9시부터 오후 6시까지입니다."},
                "error": None,
            },
            "final_response": None,
        },
    ]

    for example in examples:
        print(run(example)["final_response"])