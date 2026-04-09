from typing import Any, Optional, TypedDict


class VisionToolResult(TypedDict):
    success: bool
    tool_name: str
    message: str
    data: dict[str, Any]
    error: Optional[str]


def vision_tool() -> VisionToolResult:
    return {
        "success": True,
        "tool_name": "vision",
        "message": "이미지 업로드 요청",
        "data": {
            "requires_image": True,
            "upload_mode": "mock",
            "guide": "사진을 보내주세요.",
        },
        "error": None,
    }