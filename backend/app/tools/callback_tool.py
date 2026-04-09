import re
from typing import Any, Optional, TypedDict


class CallbackToolResult(TypedDict):
    success: bool
    tool_name: str
    message: str
    data: dict[str, Any]
    error: Optional[str]


def _normalize_phone(phone: str) -> str:
    return re.sub(r"[^0-9]", "", phone)


def _mask_phone(phone: str) -> str:
    digits = _normalize_phone(phone)
    if len(digits) == 11:
        return f"{digits[:3]}-****-{digits[7:]}"
    if len(digits) == 10:
        return f"{digits[:3]}-{digits[3:6]}-****"
    return "비공개"


def callback_tool(name: str, phone: str) -> CallbackToolResult:
    clean_name = name.strip()
    clean_phone = _normalize_phone(phone)

    if not clean_name:
        return {
            "success": False,
            "tool_name": "callback",
            "message": "콜백 등록 실패",
            "data": {},
            "error": "이름이 비어 있습니다.",
        }

    if len(clean_phone) not in (10, 11):
        return {
            "success": False,
            "tool_name": "callback",
            "message": "콜백 등록 실패",
            "data": {},
            "error": "전화번호 형식이 올바르지 않습니다.",
        }

    return {
        "success": True,
        "tool_name": "callback",
        "message": "콜백 등록 성공",
        "data": {
            "status": "registered",
            "name": clean_name,
            "phone": clean_phone,
            "masked_phone": _mask_phone(clean_phone),
        },
        "error": None,
    }