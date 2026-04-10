from __future__ import annotations

from typing import Any


def vision_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    이미지/스크린샷 확인이 필요한 요청을 처리하는 노드.

    현재 단계의 역할
    ---------------
    - 실제 비전 모델 추론은 하지 않는다.
    - '이미지 업로드/전달이 필요하다'는 액션 결과를 구조화해 state에 저장한다.
    - response_node가 이를 읽고 자연스럽게 사용자에게 안내하도록 한다.

    향후 확장 방향
    --------------
    - SMS 링크 발송
    - 이미지 업로드 URL 생성
    - 제품 라벨 OCR
    - 제품 식별(product_identify)
    - 앱 화면 가이드(app_guide)

    지금은 그 전 단계인 'vision request action'으로 본다.
    """

    user_input = (state.get("user_input") or "").strip()

    action_result = {
        "success": True,
        "action_type": "vision_request",
        "message": (
            "정확한 안내를 위해 사진이나 이미지를 먼저 확인해야 합니다. "
            "관련 이미지나 스크린샷을 보내주시면 이어서 도와드리겠습니다."
        ),
        "requires_image": True,
        "request_type": _infer_vision_request_type(user_input),
        "upload_method": "manual_upload",
        "upload_url": None,
    }

    print("\n[VISION NODE]")
    print("request_type:", action_result.get("request_type"))

    debug_info = dict(state.get("debug_info") or {})
    debug_info["vision_node"] = {
        "action": "vision_request",
        "request_type": action_result["request_type"],
        "requires_image": True,
    }

    return {
        **state,
        "action_result": action_result,
        # 하위호환용 legacy 필드
        "tool_result": action_result["message"],
        "debug_info": debug_info,
    }


def _infer_vision_request_type(user_input: str) -> str:
    """
    사용자 입력을 보고 어떤 종류의 이미지 요청인지 아주 간단히 추론한다.

    현재는 rule-based로 최소 분류만 한다.
    나중에 product_identify / app_guide / OCR 분기로 확장 가능하다.
    """
    text = (user_input or "").lower()

    if any(keyword in text for keyword in ["스크린샷", "화면", "캡처", "앱"]):
        return "screen_capture"

    if any(keyword in text for keyword in ["라벨", "모델명", "제품", "기기", "시리얼"]):
        return "product_label"

    if any(keyword in text for keyword in ["사진", "이미지", "첨부"]):
        return "general_image"

    return "unknown_image"