from typing import Any, Optional, TypedDict


class FAQToolResult(TypedDict):
    success: bool
    tool_name: str
    message: str
    data: dict[str, Any]
    error: Optional[str]


def faq_tool(query: str) -> FAQToolResult:
    clean_query = query.strip()

    return {
        "success": True,
        "tool_name": "faq",
        "message": "FAQ 조회 성공",
        "data": {
            "matched_topic": "operating_hours",
            "answer": "운영시간은 09:00~18:00 입니다.",
            "original_query": clean_query,
        },
        "error": None,
    }