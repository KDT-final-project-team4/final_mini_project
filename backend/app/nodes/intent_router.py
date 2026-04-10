from __future__ import annotations

import json
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.config import get_router_model


# --------------------------------------------------------------
# Intent Router 전용 LLM
# --------------------------------------------------------------
# 목적:
# - 짧은 입력 기반 intent 분류
# - 비용/속도 우선
# - 나중에 Gemma 4 비교 실험 시 이 모델만 쉽게 바꿀 수 있게 함
_router_llm = ChatOpenAI(
    model=get_router_model(),
    temperature=0,
)


SUPPORTED_INTENTS = {
    "faq",
    "callback",
    "vision_needed",
    "unsupported",
}


def intent_router(state: dict[str, Any]) -> dict[str, Any]:
    """
    사용자 입력을 intent로 분류하는 노드.

    현재 지원 intent
    ----------------
    - faq
    - callback
    - vision_needed
    - unsupported

    설계 원칙
    ----------
    1. callback 멀티턴 흐름이 이미 활성화된 경우에는 새로 intent를 재분류하지 않고 callback 유지
    2. 분류 결과가 이상하거나 실패하면 unsupported로 안전 fallback
    3. intent 분류 설명(reason)은 debug_info에 남겨 추후 실험/비교에 활용
    """

    user_input = (
        state.get("user_input")
        or state.get("question")
        or state.get("message")
        or state.get("last_user_message")
        or ""
    ).strip()

    active_flow = (state.get("active_flow") or "").strip()

    # --------------------------------------------------------------
    # 1. 이미 callback 흐름 중이면 intent 재분류하지 않음
    # --------------------------------------------------------------
    # 예:
    # - "콜백 부탁드려요" 이후
    # - 이름 입력
    # - 전화번호 입력
    #
    # 이런 상황에서 다시 faq나 unsupported로 튀면 안 되므로
    # active_flow가 callback이면 callback으로 강제 유지
    if active_flow == "callback":
        debug_info = dict(state.get("debug_info") or {})
        debug_info["intent_router"] = {
            "source": "active_flow_override",
            "intent": "callback",
            "reason": "active_flow is already callback",
        }

        return {
            **state,
            "intent": "callback",
            "debug_info": debug_info,
        }

    # 입력이 비어 있으면 unsupported 처리
    if not user_input:
        debug_info = dict(state.get("debug_info") or {})
        debug_info["intent_router"] = {
            "source": "empty_input",
            "intent": "unsupported",
            "reason": "user_input is empty",
        }

        return {
            **state,
            "intent": "unsupported",
            "debug_info": debug_info,
        }

    # --------------------------------------------------------------
    # 2. LLM 기반 intent 분류
    # --------------------------------------------------------------
    system_prompt = """
        너는 고객상담 시스템의 Intent Router다.

        사용자 입력을 아래 네 가지 intent 중 하나로만 분류해야 한다.

        1. faq
        - 매뉴얼/정책/운영 절차/이용 방법/조건/환불/교환/취소/배송 등
        문서 검색 기반으로 답할 수 있는 일반 질문

        2. callback
        - 담당자 연락 요청
        - 다시 전화 요청
        - 콜백 접수
        - 전화번호를 남기고 연락 달라는 요청

        3. vision_needed
        - 사진, 이미지, 스크린샷, 제품 라벨, 화면 캡처 등을
        확인해야 더 정확히 안내할 수 있는 경우

        4. unsupported
        - 위 셋에 해당하지 않거나,
        의도가 너무 불명확하거나,
        현재 시스템이 처리하기 어려운 경우

        반드시 아래 JSON 형식으로만 답해라.
        {
        "intent": "faq | callback | vision_needed | unsupported",
        "reason": "짧은 분류 근거"
        }
    """

    human_prompt = f"""
        사용자 입력: {user_input}
    """

    try:
        response = _router_llm.invoke(
            [
                SystemMessage(content=system_prompt.strip()),
                HumanMessage(content=human_prompt.strip()),
            ]
        )

        raw_content = (response.content or "").strip()
        parsed = _safe_parse_intent_json(raw_content)

        predicted_intent = parsed.get("intent", "unsupported")
        reason = parsed.get("reason", "분류 사유 없음")

        if predicted_intent not in SUPPORTED_INTENTS:
            predicted_intent = "unsupported"
            reason = f"지원하지 않는 intent가 반환되어 unsupported로 처리: {reason}"

        print("\n[INTENT ROUTER]")
        print("input:", user_input)
        print("predicted_intent:", predicted_intent)

        debug_info = dict(state.get("debug_info") or {})
        debug_info["intent_router"] = {
            "source": "llm",
            "model": get_router_model(),
            "intent": predicted_intent,
            "reason": reason,
            "raw_response": raw_content,
        }

        return {
            **state,
            "intent": predicted_intent,
            "debug_info": debug_info,
        }

    except Exception as error:
        # ----------------------------------------------------------
        # 3. LLM 실패 시 안전 fallback
        # ----------------------------------------------------------
        debug_info = dict(state.get("debug_info") or {})
        debug_info["intent_router"] = {
            "source": "exception_fallback",
            "model": get_router_model(),
            "intent": "unsupported",
            "reason": f"intent router failed: {error}",
        }

        return {
            **state,
            "intent": "unsupported",
            "debug_info": debug_info,
        }


def _safe_parse_intent_json(raw_text: str) -> dict[str, Any]:
    """
    LLM 응답을 최대한 안전하게 JSON으로 파싱한다.

    기대 형식:
    {
        "intent": "...",
        "reason": "..."
    }

    모델이 코드블록으로 감싸거나 잡텍스트를 섞을 수 있으므로
    간단한 정리 후 파싱한다.
    """
    cleaned = raw_text.strip()

    # ```json ... ``` 형태 제거
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json", "", 1).strip()

    # 가장 단순한 JSON 파싱 시도
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    # JSON 블록 추출 재시도
    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start != -1 and end != -1 and start < end:
        candidate = cleaned[start : end + 1]
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass

    # 끝까지 실패하면 unsupported fallback용 구조 반환
    return {
        "intent": "unsupported",
        "reason": "JSON 파싱 실패",
    }