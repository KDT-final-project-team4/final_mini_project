"""
Twilio 음성 웹훅, Media Stream WebSocket, STT(Deepgram), LLM 응답(Gemini), TTS(ElevenLabs).
"""

import base64
import html
import json
import os

import requests
from elevenlabs import ElevenLabs
from fastapi import APIRouter, Request, Response, WebSocket
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

router = APIRouter()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
# ElevenLabs 대시보드의 Voice ID (기본: Rachel 예시 ID)
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
LLM_MODEL = "models/gemini-2.5-flash"
LLM_SYSTEM_PROMPT = """
당신은 매우 유능하고 똑똑한 상담원입니다.
사용자의 질문에 너무 장황하지 않게만 대답해 주세요.

현재 들어온 질문만으로 대답을 생성해 내는 것이 어렵다면
이전 질문들을 참고하여 대답을 생성해 내세요.

사용자 질문:
{user_speech}

이전 질문들:
{previous_speech_data}
"""

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# LangGraph 콜백 플로우(dialogue_manager)에서 설정한 tool_result 안내 문구 — /voice Say에 사용
_PENDING_VOICE_SAY: str | None = "상담원 연결 중입니다. 잠시만 기다려 주세요."


def publish_voice_say(text: str | None) -> None:
    """콜백 노드 이후 대화 노드에서 호출. Twilio /voice 의 <Say> 기본 문구로 쓸 수 있음."""
    global _PENDING_VOICE_SAY
    if text is None:
        _PENDING_VOICE_SAY = "상담원 연결 중입니다. 잠시만 기다려 주세요."
    else:
        s = str(text).strip()
        _PENDING_VOICE_SAY = s if s else "상담원 연결 중입니다. 잠시만 기다려 주세요."


def resolve_voice_say_text(request: Request) -> str:
    """쿼리 → 그래프에서 넣은 pending → 환경변수 → 하드코딩 순."""
    q = request.query_params.get("say_text")
    if q and q.strip():
        return q.strip()
    return _PENDING_VOICE_SAY


class CounselContent:
    def __init__(self, user_speech, pre_user_speech, ai_response, pre_ai_response):
        self.user_speech = user_speech
        self.pre_user_speech = pre_user_speech
        self.ai_response = ai_response
        self.pre_ai_response = pre_ai_response


def generate_response(transcript, previous_speech_data):
    llm = ChatGoogleGenerativeAI(model=LLM_MODEL, api_key=GEMINI_API_KEY)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", LLM_SYSTEM_PROMPT),
            ("user", "사용자 질문: {transcript}"),
            ("user", "이전 질문들: {previous_speech_data}"),
        ]
    )
    chain = prompt | llm
    response = chain.invoke(
        {"user_speech": transcript, "previous_speech_data": previous_speech_data}
    )
    return response.content


def ai_text_response_to_audio(text):
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    chunks = client.text_to_speech.convert(
        voice_id=ELEVENLABS_VOICE_ID,
        text=text,
        model_id="eleven_multilingual_v2",
    )
    return b"".join(chunks)


def get_user_input_to_text(audio_chunk):
    try:
        if not DEEPGRAM_API_KEY:
            raise RuntimeError("DEEPGRAM_API_KEY가 설정되어 있지 않습니다. (.env 확인)")

        url = "https://api.deepgram.com/v1/listen"
        params = {
            "model": "nova-2",
            "language": "ko",
            "encoding": "mulaw",
            "sample_rate": 8000,
            "channels": 1,
            "punctuate": "true",
        }
        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": "audio/x-mulaw",
        }

        resp = requests.post(url, params=params, headers=headers, data=audio_chunk, timeout=30)
        resp.raise_for_status()
        result = resp.json()

        transcript = (
            result.get("results", {})
            .get("channels", [{}])[0]
            .get("alternatives", [{}])[0]
            .get("transcript", "")
        )
        print(f"음성 인식 결과: {transcript}")
        print(f"음성 인식 결과 raw 디버깅: {result}")

        return transcript

    except Exception as e:
        print(f"speech_to_text 예외 발생: {e}")
        return None


@router.api_route("/voice", methods=["GET", "POST"])
async def voice_webhook(request: Request):
    say_text = resolve_voice_say_text(request)
    safe_say = html.escape(say_text, quote=False)
    stream_url = "wss://ferly-coxcombic-elroy.ngrok-free.dev/media-stream"
    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Say language="ko-KR">{safe_say}</Say>
        <Connect>
            <Stream url="{html.escape(stream_url, quote=True)}" />
        </Connect>
    </Response>
    """

    return Response(content=twiml_response, media_type="application/xml")


@router.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    await websocket.accept()
    print("Twilio 오디오 스트림 연결 성공")

    counsel_content = CounselContent(None, [], None, [])
    stream_sid = None

    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)

            event_type = data["event"]

            if event_type == "start":
                stream_sid = data["start"]["streamSid"]
                print(f"▶ 스트림 시작 (StreamSid: {stream_sid})")

            elif event_type == "media":
                payload = data["media"]["payload"]
                audio_chunk = base64.b64decode(payload)
                print(f"받은 오디오 크기: {len(audio_chunk)} bytes")

                transcript = get_user_input_to_text(audio_chunk)
                if not transcript:
                    continue

                counsel_content.user_speech = transcript
                counsel_content.pre_user_speech.append(transcript)

                agent_response = generate_response(transcript, counsel_content.pre_user_speech)

                if agent_response:
                    counsel_content.ai_response = agent_response
                    counsel_content.pre_ai_response.append(agent_response)

                    audio_chunk = ai_text_response_to_audio(agent_response)
                    if audio_chunk:
                        if isinstance(audio_chunk, (bytes, bytearray)):
                            raw_audio = bytes(audio_chunk)
                        else:
                            raw_audio = bytes(audio_chunk)

                        encoded_audio = base64.b64encode(raw_audio).decode("ascii")
                        if not stream_sid:
                            print("streamSid가 없어 Twilio로 오디오 전송을 건너뜁니다.")
                            continue

                        outbound_message = {
                            "event": "media",
                            "streamSid": stream_sid,
                            "media": {"payload": encoded_audio},
                        }
                        await websocket.send_text(json.dumps(outbound_message))
                    else:
                        print("TTS 변환 실패")

                else:
                    counsel_content.ai_response = "응답 생성 실패"
                    print(f"응답 생성 실패: {agent_response}")

                print(f"유저 발화: {counsel_content.user_speech}")
                print(f"이전 유저 발화: {counsel_content.pre_user_speech}")
                print(f"현재 agent 응답 데이터: {counsel_content.ai_response}")
                print(f"이전 agent 응답 데이터: {counsel_content.pre_ai_response}")

            elif event_type == "stop":
                print("스트림 종료")
                break

    except Exception as e:
        print(f"에러 발생: {e}")

    finally:
        await websocket.close()
