# backend/tests/test_tools.py
# 실행
# - cd backend
# - python -m tests.test_tools

from app.tools.callback_tool import callback_tool
from app.tools.faq_tool import faq_tool
from app.tools.vision_tool import vision_tool


def test_faq_tool() -> None:
    result = faq_tool("운영시간 알려줘")

    assert result["success"] is True
    assert result["tool_name"] == "faq"
    assert result["message"] == "FAQ 조회 성공"
    assert result["error"] is None

    assert "data" in result
    assert result["data"]["matched_topic"] == "operating_hours"
    assert result["data"]["answer"] == "운영시간은 09:00~18:00 입니다."
    assert result["data"]["original_query"] == "운영시간 알려줘"


def test_callback_tool_success() -> None:
    result = callback_tool("홍길동", "010-1234-5678")

    assert result["success"] is True
    assert result["tool_name"] == "callback"
    assert result["message"] == "콜백 등록 성공"
    assert result["error"] is None

    assert "data" in result
    assert result["data"]["status"] == "registered"
    assert result["data"]["name"] == "홍길동"
    assert result["data"]["phone"] == "01012345678"
    assert "masked_phone" in result["data"]


def test_callback_tool_invalid_phone() -> None:
    result = callback_tool("홍길동", "123")

    assert result["success"] is False
    assert result["tool_name"] == "callback"
    assert result["message"] == "콜백 등록 실패"
    assert result["data"] == {}
    assert result["error"] == "전화번호 형식이 올바르지 않습니다."


def test_callback_tool_empty_name() -> None:
    result = callback_tool("", "010-1234-5678")

    assert result["success"] is False
    assert result["tool_name"] == "callback"
    assert result["message"] == "콜백 등록 실패"
    assert result["data"] == {}
    assert result["error"] == "이름이 비어 있습니다."


def test_vision_tool() -> None:
    result = vision_tool()

    assert result["success"] is True
    assert result["tool_name"] == "vision"
    assert result["message"] == "이미지 업로드 요청"
    assert result["error"] is None

    assert "data" in result
    assert result["data"]["requires_image"] is True
    assert result["data"]["upload_mode"] == "mock"
    assert result["data"]["guide"] == "사진을 보내주세요."


def run_all_tests() -> None:
    test_faq_tool()
    print("test_faq_tool 통과")

    test_callback_tool_success()
    print("test_callback_tool_success 통과")

    test_callback_tool_invalid_phone()
    print("test_callback_tool_invalid_phone 통과")

    test_callback_tool_empty_name()
    print("test_callback_tool_empty_name 통과")

    test_vision_tool()
    print("test_vision_tool 통과")

    print("모든 tool 테스트 통과")


if __name__ == "__main__":
    run_all_tests()