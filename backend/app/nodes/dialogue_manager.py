import os
from urllib.parse import urlencode
import requests
from app.tools.dialogue_tool import publish_voice_say

# 콜백 플로우: tool_result를 Twilio <Say>용으로 넣고, /chat 응답 문자열도 맞춘다.

# /voice 는 원래 Twilio 서버가 호출하는 웹훅이다. 같은 프로세스에서 "미리 한 번 불러보기"만 할 때는
# 아래 PING_VOICE_WEBHOOK 를 켜면 된다 (전화가 자동으로 걸리지는 않음).


def _missing_callback_message(state: dict) -> str:
    name = state.get("collected_name")
    phone = state.get("collected_phone")
    if not name and not phone:
        return (
            "콜백 접수를 위해 성함과 휴대폰 번호를 알려 주세요. "
            "예: 홍길동 010-1234-5678 처럼 한 줄로 보내 주셔도 됩니다."
        )
    if not name:
        return (
            "성함을 알려 주세요. (이미 전화번호를 보내 주셨다면 성함만 입력해 주세요.)"
        )
    if not phone:
        return "휴대폰 번호를 알려 주세요. (예: 01012345678 또는 010-1234-5678)"
    return None


def run(state):

    is_missing = _missing_callback_message(state)
    print(f"is_missing: {is_missing}")

    if is_missing is not None:
        return {"tool_result": is_missing}

    return {
        "tool_result": state.get("tool_result"),
        "collected_name": state.get("collected_name"),
        "collected_phone": state.get("collected_phone"),
        "final_response": state.get("final_response"),
        "user_input": state.get("user_input"),
        "intent": state.get("intent"),
        "next_action": state.get("next_action"),
    }
