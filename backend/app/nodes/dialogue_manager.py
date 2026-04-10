from __future__ import annotations

import re
from typing import Any


def dialogue_manager(state: dict[str, Any]) -> dict[str, Any]:
    """
    현재 대화 상태를 바탕으로 다음 행동(next_action)을 결정하는 노드.

    현재 책임
    --------
    1. intent를 보고 FAQ / callback / vision / unsupported 중 어느 흐름으로 갈지 결정
    2. callback 흐름이면 이름/전화번호 수집 상태를 확인
    3. active_flow를 적절히 유지/정리
    4. debug_info에 결정 근거를 남김

    설계 원칙
    ----------
    - 이 노드는 '실행'이 아니라 '흐름 결정'만 담당한다.
    - callback은 slot filling 흐름으로 취급한다.
    - 앞으로 business action / identity verify / app guide 같은 노드가 추가되어도
      이 노드의 역할은 "현재 state를 보고 다음 step 결정"으로 유지된다.
    """

    intent = (state.get("intent") or "").strip()
    user_input = (state.get("user_input") or "").strip()
    active_flow = (state.get("active_flow") or "").strip()

    collected_name = (state.get("collected_name") or "").strip()
    collected_phone = (state.get("collected_phone") or "").strip()

    slots = dict(state.get("slots") or {})

    # --------------------------------------------------------------
    # 1. callback 흐름 상태 동기화
    # --------------------------------------------------------------
    # 기존 collected_* 필드와 slots를 함께 운용할 수 있게 맞춘다.
    if collected_name and not slots.get("name"):
        slots["name"] = collected_name

    if collected_phone and not slots.get("phone"):
        slots["phone"] = collected_phone

    collected_name = (slots.get("name") or collected_name or "").strip()
    collected_phone = (slots.get("phone") or collected_phone or "").strip()

    # --------------------------------------------------------------
    # 2. intent별 다음 행동 결정
    # --------------------------------------------------------------
    if intent == "callback" or active_flow == "callback":
        next_action, updated_flow, updated_slots = _decide_callback_action(
            user_input=user_input,
            active_flow=active_flow,
            collected_name=collected_name,
            collected_phone=collected_phone,
            slots=slots,
        )

        print("\n[DIALOGUE MANAGER]")
        print("intent:", intent)
        print("next_action:", next_action)
        print("slots:", updated_slots)

        debug_info = dict(state.get("debug_info") or {})
        debug_info["dialogue_manager"] = {
            "intent": intent,
            "next_action": next_action,
            "active_flow": updated_flow,
            "reason": _build_callback_reason(
                next_action=next_action,
                collected_name=collected_name,
                collected_phone=collected_phone,
            ),
        }

        return {
            **state,
            "next_action": next_action,
            "active_flow": updated_flow,
            "collected_name": updated_slots.get("name", ""),
            "collected_phone": updated_slots.get("phone", ""),
            "slots": updated_slots,
            "debug_info": debug_info,
        }

    if intent == "faq":
        print("\n[DIALOGUE MANAGER]")
        print("intent:", intent)
        print("next_action:", "route_faq")
        print("slots:", slots)

        debug_info = dict(state.get("debug_info") or {})
        debug_info["dialogue_manager"] = {
            "intent": intent,
            "next_action": "route_faq",
            "active_flow": "",
            "reason": "문서 기반 검색 응답 흐름으로 라우팅",
        }

        return {
            **state,
            "next_action": "route_faq",
            "active_flow": "",
            "slots": slots,
            "debug_info": debug_info,
        }

    if intent == "vision_needed":
        print("\n[DIALOGUE MANAGER]")
        print("intent:", intent)
        print("next_action:", "route_vision")
        print("slots:", slots)

        debug_info = dict(state.get("debug_info") or {})
        debug_info["dialogue_manager"] = {
            "intent": intent,
            "next_action": "route_vision",
            "active_flow": "",
            "reason": "이미지/스크린샷 확인이 필요한 요청으로 판단",
        }

        return {
            **state,
            "next_action": "route_vision",
            "active_flow": "",
            "slots": slots,
            "debug_info": debug_info,
        }

    # --------------------------------------------------------------
    # 3. unsupported 또는 분류 불명확 상황
    # --------------------------------------------------------------
    print("\n[DIALOGUE MANAGER]")
    print("intent:", intent or "unknown")
    print("next_action:", "route_unsupported")
    print("slots:", slots)

    debug_info = dict(state.get("debug_info") or {})
    debug_info["dialogue_manager"] = {
        "intent": intent or "unknown",
        "next_action": "route_unsupported",
        "active_flow": "",
        "reason": "지원하지 않는 의도이거나 분류가 불명확하여 fallback 처리",
    }

    return {
        **state,
        "next_action": "route_unsupported",
        "active_flow": "",
        "slots": slots,
        "debug_info": debug_info,
    }


def _decide_callback_action(
    user_input: str,
    active_flow: str,
    collected_name: str,
    collected_phone: str,
    slots: dict[str, Any],
) -> tuple[str, str, dict[str, Any]]:
    """
    callback 흐름의 다음 행동을 결정한다.

    반환값
    ------
    (next_action, updated_active_flow, updated_slots)

    callback 흐름 규칙
    ------------------
    1. 아직 이름이 없으면 ask_name
    2. 이름은 있는데 전화번호가 없으면 ask_phone
    3. 이름/전화번호 모두 있으면 route_callback
    """

    updated_slots = dict(slots)

    # active_flow가 비어 있어도 callback intent면 callback flow 시작
    updated_active_flow = "callback"

    # --------------------------------------------------------------
    # 1. 이름이 아직 없는 경우
    # --------------------------------------------------------------
    if not collected_name:
        # 사용자가 이름 질문 단계에서 바로 이름을 입력했을 가능성 처리
        maybe_name = _extract_possible_name(user_input)
        if maybe_name:
            updated_slots["name"] = maybe_name
            collected_name = maybe_name

        # 여전히 이름이 없으면 ask_name
        if not collected_name:
            return "ask_name", updated_active_flow, updated_slots

    # --------------------------------------------------------------
    # 2. 전화번호가 아직 없는 경우
    # --------------------------------------------------------------
    if not collected_phone:
        maybe_phone = _extract_phone_number(user_input)
        if maybe_phone:
            updated_slots["phone"] = maybe_phone
            collected_phone = maybe_phone

        if not collected_phone:
            return "ask_phone", updated_active_flow, updated_slots

    # --------------------------------------------------------------
    # 3. 둘 다 모였으면 callback 실행 단계로 이동
    # --------------------------------------------------------------
    return "route_callback", updated_active_flow, updated_slots


def _extract_possible_name(user_input: str) -> str:
    """
    아주 단순한 이름 후보 추출.

    목적
    ----
    callback 흐름에서 사용자가
    - "홍길동입니다"
    - "김민수요"
    - "제 이름은 박서준입니다"
    처럼 답했을 때 이름을 느슨하게 잡아보는 보조 함수.

    주의
    ----
    완벽한 NER이 아니라 보조 휴리스틱 수준이다.
    이상한 값이 들어올 수 있으므로 너무 공격적으로 추출하지 않는다.
    """
    text = (user_input or "").strip()
    if not text:
        return ""

    # 전화번호가 섞인 경우는 이름으로 보지 않음
    if re.search(r"\d{2,4}[- ]?\d{3,4}[- ]?\d{4}", text):
        return ""

    # 너무 긴 문장은 이름으로 보지 않음
    if len(text) > 12:
        return ""
    
    # 콜백 요청 문장/일반 서술문에서 자주 나오는 비이름 표현 제외
    blocked_keywords = [
        "싶어", "싶어요", "해주세요", "부탁", "연락", "통화", "상담",
        "문의", "도와", "가능", "맞아", "아니", "네", "응",
    ]
    if any(keyword in text for keyword in blocked_keywords):
        # 단, 아래 명시 패턴에서 다시 잡히는 경우는 허용
        pass

    patterns = [
        r"제 이름은\s*([가-힣]{2,4})\s*(?:입니다|이에요|예요)?$",
        r"이름은\s*([가-힣]{2,4})\s*(?:입니다|이에요|예요)?$",
        r"성함은\s*([가-힣]{2,4})\s*(?:입니다|이에요|예요)?$",
        r"^([가-힣]{2,4})입니다$",
        r"^([가-힣]{2,4})이에요$",
        r"^([가-힣]{2,4})예요$",
        r"^([가-힣]{2,4})$",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            candidate = match.group(1).strip()

            if candidate in {
                "싶어", "문의", "상담", "연락", "통화", "부탁", "도움", "가능"
            }:
                return ""

            return candidate

    return ""


def _extract_phone_number(user_input: str) -> str:
    """
    입력에서 전화번호 후보를 추출하고 표준 형태로 정리한다.

    반환 형식:
    - 010-1234-5678
    - 02-123-4567
    """
    text = (user_input or "").strip()
    if not text:
        return ""

    digits = re.sub(r"[^\d]", "", text)

    # 휴대폰
    if len(digits) == 11 and digits.startswith("010"):
        return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"

    # 서울 지역번호 등 일반 전화
    if len(digits) == 9 and digits.startswith("02"):
        return f"{digits[:2]}-{digits[2:5]}-{digits[5:]}"
    if len(digits) == 10 and digits.startswith("02"):
        return f"{digits[:2]}-{digits[2:6]}-{digits[6:]}"
    if len(digits) == 10 and not digits.startswith("02"):
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    if len(digits) == 11 and not digits.startswith("010"):
        return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"

    return ""


def _build_callback_reason(
    next_action: str,
    collected_name: str,
    collected_phone: str,
) -> str:
    """
    debug_info 기록용 callback 결정 사유 생성.
    """
    if next_action == "ask_name":
        return "callback 흐름이며 이름 슬롯이 비어 있어 성함 수집 필요"
    if next_action == "ask_phone":
        return (
            f"callback 흐름이며 이름은 확보됨('{collected_name}'), "
            "전화번호 슬롯이 비어 있어 연락처 수집 필요"
        )
    if next_action == "route_callback":
        return (
            f"callback 흐름이며 이름('{collected_name}')과 "
            f"전화번호('{collected_phone}')가 모두 확보되어 접수 단계로 이동"
        )
    return "callback 흐름 처리 중"