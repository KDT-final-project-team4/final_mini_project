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
        return "성함을 알려 주세요. (이미 전화번호를 보내 주셨다면 성함만 입력해 주세요.)"
    return "휴대폰 번호를 알려 주세요. (예: 01012345678 또는 010-1234-5678)"
 

def run(state): 
    first_dialogue = state.get("tool_result")

    # CALLBACK_NODE에서만 들어옴. tool_result가 없으면 이름/전화 미수집(또는 도구 실패)
    if not first_dialogue:
        text = _missing_callback_message(state)
        publish_voice_say(text)
    else:
        publish_voice_say(str(first_dialogue).strip())
        text = str(first_dialogue).strip()

    # 선택: 로컬에서 TwiML이 나오는지 확인만 할 때 (Twilio 통화 트리거 아님)
    if os.getenv("PING_VOICE_WEBHOOK", "").lower() in ("1", "true", "yes"):
        base = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
        qs = urlencode({"say_text": text})
        try:
            requests.get(f"{base}/voice?{qs}", timeout=5)
            print(f"TwiML 요청 성공: {base}/voice?{qs}")
        except requests.RequestException:
            pass

    return {
        "final_response": text,
    }
