from __future__ import annotations

import json
import os
from typing import Any, Final

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None  # type: ignore

try:
    from app.state import CallFlowState
    from app.config import get_logger
    from app.prompts.intent_router_prompt import (
        INTENT_JSON_SCHEMA,
        INTENT_ROUTER_SYSTEM_PROMPT,
        build_intent_router_user_prompt,
    )
except ImportError:  # local test fallback
    from state import CallFlowState
    from config import get_logger
    from intent_router_prompt import (
        INTENT_JSON_SCHEMA,
        INTENT_ROUTER_SYSTEM_PROMPT,
        build_intent_router_user_prompt,
    )


logger = get_logger(__name__)

FAQ_KEYWORDS: Final[tuple[str, ...]] = (
    "운영시간",
    "영업시간",
    "운영 시간",
    "영업 시간",
    "몇 시",
    "오픈",
    "마감",
)

CALLBACK_KEYWORDS: Final[tuple[str, ...]] = (
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

VISION_KEYWORDS: Final[tuple[str, ...]] = (
    "사진",
    "이미지",
    "첨부",
    "봐줘",
    "확인해줘",
    "고장",
    "오류",
    "문제",
    "이거 이상",
    "불량",
)

ALLOWED_INTENTS: Final[set[str]] = {"faq", "callback", "vision", "unknown"}


def _state_summary(state: CallFlowState) -> dict:
    return {
        "session_id": state.get("session_id"),
        "user_input": state.get("user_input"),
        "intent": state.get("intent"),
        "active_flow": state.get("active_flow"),
        "awaiting_field": state.get("awaiting_field"),
        "collected_name": state.get("collected_name"),
        "collected_phone": state.get("collected_phone"),
    }


def _normalize_text(text: str) -> str:
    return (text or "").strip().lower()


def _contains_keyword(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def _is_callback_in_progress(state: CallFlowState) -> bool:
    return (
        state.get("active_flow") == "callback"
        or state.get("awaiting_field") in ("name", "phone")
    )


def _has_image(state: CallFlowState) -> bool:
    """
    state 구조가 아직 완전히 확정되지 않았으므로
    자주 쓰는 이미지 관련 키를 넓게 확인한다.
    """
    image_like_keys = (
        "has_image",
        "image_path",
        "image_url",
        "image_b64",
        "image_base64",
        "image_bytes",
        "uploaded_image",
    )

    for key in image_like_keys:
        value = state.get(key)  # type: ignore[arg-type]
        if value:
            return True
    return False


def _safe_confidence(value: Any) -> float:
    try:
        num = float(value)
    except Exception:
        return 0.0

    if num < 0:
        return 0.0
    if num > 1:
        return 1.0
    return num


def classify_intent(user_input: str) -> str:
    """
    기존 rule-based intent 분류

    우선순위
    1. callback
    2. faq
    3. vision
    4. unknown
    """
    text = _normalize_text(user_input)

    if not text:
        return "unknown"

    if _contains_keyword(text, CALLBACK_KEYWORDS):
        return "callback"

    if _contains_keyword(text, FAQ_KEYWORDS):
        return "faq"

    if _contains_keyword(text, VISION_KEYWORDS):
        return "vision"

    return "unknown"


def _get_openai_client() -> OpenAI | None:
    if OpenAI is None:
        logger.warning("intent_router.openai_sdk_missing fallback_to_rule_based=True")
        return None

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        logger.warning("intent_router.api_key_missing fallback_to_rule_based=True")
        return None

    return OpenAI(api_key=api_key)


def _get_intent_model_name() -> str | None:
    model = os.getenv("OPENAI_INTENT_MODEL", "").strip()
    if not model:
        logger.warning("intent_router.model_missing OPENAI_INTENT_MODEL is empty")
        return None
    return model


def _call_llm_intent_router(state: CallFlowState) -> dict[str, Any] | None:
    client = _get_openai_client()
    model = _get_intent_model_name()

    if client is None or model is None:
        return None

    user_prompt = build_intent_router_user_prompt(
        user_message=state.get("user_input", "") or "",
        has_image=_has_image(state),
        active_flow=state.get("active_flow"),
        awaiting_field=state.get("awaiting_field"),
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
                            "text": INTENT_ROUTER_SYSTEM_PROMPT,
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
            text={
                "format": {
                    "type": "json_schema",
                    "name": "intent_router_output",
                    "strict": True,
                    "schema": INTENT_JSON_SCHEMA,
                }
            },
        )

        output_text = (response.output_text or "").strip()
        if not output_text:
            logger.warning("intent_router.llm_empty_output")
            return None

        parsed = json.loads(output_text)
        if not isinstance(parsed, dict):
            logger.warning("intent_router.llm_non_dict_output output=%s", output_text)
            return None

        intent = str(parsed.get("intent", "")).strip()
        confidence = _safe_confidence(parsed.get("confidence"))
        reason = str(parsed.get("reason", "")).strip()

        if intent not in ALLOWED_INTENTS:
            logger.warning("intent_router.llm_invalid_intent intent=%s", intent)
            return None

        return {
            "intent": intent,
            "confidence": confidence,
            "reason": reason or "llm classified intent",
        }

    except Exception as exc:
        logger.exception("intent_router.llm_exception error=%s", exc)
        return None


def _fallback_intent(state: CallFlowState) -> str:
    """
    LLM 실패 시 기존 규칙으로 복귀한다.
    """
    user_input = state.get("user_input", "") or ""
    return classify_intent(user_input)


def run(state: CallFlowState) -> CallFlowState:
    logger.info("intent_router.enter state=%s", _state_summary(state))

    # 1) callback 진행 중이면 절대 흐름을 깨지 않는다.
    if _is_callback_in_progress(state):
        state["intent"] = "callback"
        logger.info("intent_router.keep_callback state=%s", _state_summary(state))
        return state

    user_input = state.get("user_input", "") or ""
    text = _normalize_text(user_input)
    has_image = _has_image(state)

    # 2) callback 의도는 rule-based 우선 유지
    if _contains_keyword(text, CALLBACK_KEYWORDS):
        state["intent"] = "callback"
        logger.info("intent_router.rule_callback state=%s", _state_summary(state))
        return state

    # 3) FAQ도 강한 규칙은 먼저 유지
    if _contains_keyword(text, FAQ_KEYWORDS):
        state["intent"] = "faq"
        logger.info("intent_router.rule_faq state=%s", _state_summary(state))
        return state

    # 4) 이미지가 실제로 있고 vision 관련 문구가 있으면 vision 우선
    if has_image and (_contains_keyword(text, VISION_KEYWORDS) or not text):
        state["intent"] = "vision"
        logger.info("intent_router.rule_vision_with_image state=%s", _state_summary(state))
        return state

    # 5) 나머지는 LLM 분류 시도
    llm_result = _call_llm_intent_router(state)
    if llm_result is not None:
        intent = llm_result["intent"]
        confidence = llm_result["confidence"]
        reason = llm_result["reason"]

        # confidence가 너무 낮으면 기존 규칙으로 fallback
        if confidence >= 0.60:
            state["intent"] = intent
            logger.info(
                "intent_router.llm_success intent=%s confidence=%.2f reason=%s state=%s",
                intent,
                confidence,
                reason,
                _state_summary(state),
            )
            return state

        logger.warning(
            "intent_router.llm_low_confidence intent=%s confidence=%.2f reason=%s",
            intent,
            confidence,
            reason,
        )

    # 6) 최종 fallback
    state["intent"] = _fallback_intent(state)
    logger.info(
        "intent_router.fallback intent=%s state=%s",
        state.get("intent"),
        _state_summary(state),
    )
    return state


intent_router = run


if __name__ == "__main__":
    examples = [
        {
            "session_id": "test-1",
            "user_input": "운영시간 알려줘",
            "intent": None,
            "next_action": None,
            "active_flow": None,
            "awaiting_field": None,
            "collected_name": None,
            "collected_phone": None,
            "tool_result": None,
            "final_response": None,
        },
        {
            "session_id": "test-2",
            "user_input": "상담원 연결해줘",
            "intent": None,
            "next_action": None,
            "active_flow": None,
            "awaiting_field": None,
            "collected_name": None,
            "collected_phone": None,
            "tool_result": None,
            "final_response": None,
        },
        {
            "session_id": "test-3",
            "user_input": "이거 뭐가 문제인지 봐줘",
            "intent": None,
            "next_action": None,
            "active_flow": None,
            "awaiting_field": None,
            "collected_name": None,
            "collected_phone": None,
            "tool_result": None,
            "final_response": None,
            "has_image": True,
        },
        {
            "session_id": "test-4",
            "user_input": "홍길동",
            "intent": None,
            "next_action": None,
            "active_flow": "callback",
            "awaiting_field": "name",
            "collected_name": None,
            "collected_phone": None,
            "tool_result": None,
            "final_response": None,
        },
    ]

    for example in examples:
        result = run(example)
        print(example["user_input"], "->", result["intent"])