from __future__ import annotations

from datetime import datetime
from typing import TypedDict


class CallbackResult(TypedDict, total=False):
    """
    callback 액션 실행 결과 구조.

    현재 단계에서는 DB 저장 없이도 일관된 결과 구조를 반환하도록 한다.
    나중에 실제 DB 저장, Slack 알림, 이메일 발송 등이 붙어도
    이 반환 형식은 그대로 유지할 수 있다.
    """

    success: bool
    action_type: str
    message: str

    # 수집된 핵심 데이터
    name: str
    phone: str

    # 확장용 메타데이터
    request_time: str
    callback_id: str | None
    saved: bool


def register_callback_tool(name: str, phone: str) -> CallbackResult:
    """
    콜백 요청을 접수하는 구조화된 액션 도구.

    현재 역할
    --------
    - 이름과 전화번호를 받아 callback 요청 결과를 구조화된 dict로 반환
    - 지금은 실제 DB 저장 없이 동작
    - 하지만 나중에 DB/알림 연동이 붙어도 동일한 인터페이스 유지 가능

    주의
    ----
    이 함수는 현재 '저장 시뮬레이션' 단계다.
    실제 저장소가 붙으면 callback_id, saved 등을 실제 값으로 교체하면 된다.
    """
    cleaned_name = (name or "").strip()
    cleaned_phone = (phone or "").strip()

    if not cleaned_name and not cleaned_phone:
        return {
            "success": False,
            "action_type": "register_callback",
            "message": "콜백 접수를 진행하려면 성함과 전화번호가 모두 필요합니다.",
            "name": "",
            "phone": "",
            "request_time": _now_iso(),
            "callback_id": None,
            "saved": False,
        }

    if not cleaned_name:
        return {
            "success": False,
            "action_type": "register_callback",
            "message": "콜백 접수를 진행하려면 성함이 필요합니다.",
            "name": "",
            "phone": cleaned_phone,
            "request_time": _now_iso(),
            "callback_id": None,
            "saved": False,
        }

    if not cleaned_phone:
        return {
            "success": False,
            "action_type": "register_callback",
            "message": f"{cleaned_name}님, 콜백 접수를 진행하려면 연락받으실 전화번호가 필요합니다.",
            "name": cleaned_name,
            "phone": "",
            "request_time": _now_iso(),
            "callback_id": None,
            "saved": False,
        }

    # --------------------------------------------------------------
    # 현재는 저장 시뮬레이션
    # --------------------------------------------------------------
    # 추후 실제 저장소(DB)가 붙으면:
    # - callback_id 생성
    # - DB insert
    # - Slack/이메일 알림
    # 등을 여기서 수행하면 된다.
    return {
        "success": True,
        "action_type": "register_callback",
        "message": (
            f"{cleaned_name}님, 콜백 요청이 접수되었습니다. "
            f"{cleaned_phone} 번호로 확인 후 연락드릴 수 있도록 전달하겠습니다."
        ),
        "name": cleaned_name,
        "phone": cleaned_phone,
        "request_time": _now_iso(),
        "callback_id": None,
        "saved": False,
    }


def callback_tool(name: str, phone: str) -> str:
    """
    기존 문자열 반환 인터페이스와의 하위호환용 래퍼.

    현재 프로젝트의 일부 코드가 callback_tool(...) -> str 을 기대할 수 있으므로
    내부적으로는 register_callback_tool()을 사용하고,
    최종 반환만 문자열로 맞춘다.
    """
    result = register_callback_tool(name=name, phone=phone)
    return result.get("message", "콜백 요청 처리 중 문제가 발생했습니다.")


def _now_iso() -> str:
    """
    현재 시각을 ISO 문자열로 반환.
    """
    return datetime.now().isoformat(timespec="seconds")