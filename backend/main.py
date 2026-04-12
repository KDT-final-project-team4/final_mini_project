from __future__ import annotations

from copy import deepcopy
from threading import Lock
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.config import get_logger, settings
from app.graph import build_graph
from app.state import AppState, make_initial_state


logger = get_logger("chat.api")

app = FastAPI(title="Final Mini Project Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chat_graph = build_graph()

SESSION_STORE: dict[str, AppState] = {}
SESSION_LOCK = Lock()


class ChatRequest(BaseModel):
    message: str = Field(..., description="사용자 입력")
    session_id: str | None = Field(default=None, description="대화 세션 ID")


def _state_summary(state: AppState) -> dict:
    return {
        "session_id": state.get("session_id"),
        "user_input": state.get("user_input"),
        "intent": state.get("intent"),
        "next_action": state.get("next_action"),
        "active_flow": state.get("active_flow"),
        "awaiting_field": state.get("awaiting_field"),
        "collected_name": state.get("collected_name"),
        "collected_phone": state.get("collected_phone"),
        "has_tool_result": state.get("tool_result") is not None,
        "final_response": state.get("final_response"),
    }


def _load_or_create_state(session_id: str) -> AppState:
    saved = SESSION_STORE.get(session_id)
    if saved is None:
        state = make_initial_state(session_id=session_id, message="")
        logger.info("main.load_state new session_id=%s", session_id)
        return state

    logger.info("main.load_state existing session_id=%s", session_id)
    return deepcopy(saved)


def _save_state(session_id: str, state: AppState) -> None:
    SESSION_STORE[session_id] = deepcopy(state)
    logger.info("main.save_state session_id=%s state=%s", session_id, _state_summary(state))


def _make_reference() -> str:
    return f"CB-{str(uuid4().int)[-6:]}"


def _to_front_payload(result: AppState) -> dict:
    intent = result.get("intent")
    next_action = result.get("next_action")
    final_response = result.get("final_response") or "응답을 생성하지 못했습니다."
    tool_result = result.get("tool_result") or {}
    tool_name = tool_result.get("tool_name")
    data = tool_result.get("data") or {}

    payload = {
        "session_id": result.get("session_id"),
        "final_response": final_response,
        "intent": intent,
        "next_action": next_action,
        "system_state": "idle",
        "open_callback_flow": False,
        "open_vision_modal": False,
        "message": {
            "type": "ai",
            "content": final_response,
            "structuredData": {
                "type": "structured",
                "data": {
                    "suggestions": [
                        "운영시간 문의",
                        "상담원 연결",
                        "문제 이미지 확인",
                    ]
                },
            },
        },
        "error": tool_result.get("error"),
    }

    if tool_name == "faq" or intent == "faq":
        answer = data.get("answer", final_response)
        matched_topic = data.get("matched_topic")
        title_map = {
            "operating_hours": "운영시간 안내",
        }

        payload["message"] = {
            "type": "ai",
            "content": "안내 내용을 확인해주세요.",
            "structuredData": {
                "type": "faq",
                "data": {
                    "title": title_map.get(matched_topic, "FAQ 안내"),
                    "steps": [answer],
                },
            },
        }
        payload["system_state"] = "idle"
        return payload

    if next_action == "ask_name":
        payload["system_state"] = "callback-flow"
        payload["open_callback_flow"] = True
        payload["message"] = {
            "type": "ai",
            "content": final_response,
            "structuredData": {
                "type": "callback",
                "data": {
                    "step": "name",
                },
            },
        }
        return payload

    if next_action == "ask_phone":
        payload["system_state"] = "collecting-info"
        payload["open_callback_flow"] = False
        payload["message"] = {
            "type": "ai",
            "content": final_response,
            "structuredData": {
                "type": "callback",
                "data": {
                    "step": "phone",
                },
            },
        }
        return payload

    if next_action == "finish" and tool_name == "callback":
        payload["system_state"] = "idle"
        payload["message"] = {
            "type": "ai",
            "content": final_response,
            "structuredData": {
                "type": "structured",
                "data": {
                    "confirmation": True,
                    "reference": _make_reference(),
                },
            },
        }
        return payload

    if next_action == "run_vision" or tool_name == "vision":
        guide = data.get("guide", final_response)
        payload["system_state"] = "waiting-image"
        payload["open_vision_modal"] = True
        payload["message"] = {
            "type": "ai",
            "content": guide,
            "structuredData": {
                "type": "vision",
                "data": {
                    "requires_image": True,
                    "upload_mode": "frontend",
                    "guide": guide,
                },
            },
        }
        return payload

    payload["system_state"] = "idle"
    payload["message"] = {
        "type": "ai",
        "content": final_response,
        "structuredData": {
            "type": "structured",
            "data": {
                "suggestions": [
                    "운영시간 문의",
                    "상담원 연결",
                    "문제 이미지 확인",
                ]
            },
        },
    }
    return payload


@app.get("/")
def health_check():
    return {
        "message": "backend is running",
        "faq_mode": settings.FAQ_MODE,
        "callback_mode": settings.CALLBACK_MODE,
        "vision_mode": settings.VISION_MODE,
        "unknown_fallback": settings.UNKNOWN_FALLBACK,
    }


@app.post("/chat")
def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid4())

    logger.info(
        "main.chat.request session_id=%s message=%s",
        session_id,
        request.message,
    )

    try:
        with SESSION_LOCK:
            state = _load_or_create_state(session_id)
            state["session_id"] = session_id
            state["user_input"] = request.message

            logger.info("main.chat.before_invoke state=%s", _state_summary(state))

            result = chat_graph.invoke(state)

            logger.info("main.chat.after_invoke state=%s", _state_summary(result))

            _save_state(session_id, result)

        payload = _to_front_payload(result)
        logger.info(
            "main.chat.response session_id=%s intent=%s next_action=%s final_response=%s",
            payload.get("session_id"),
            payload.get("intent"),
            payload.get("next_action"),
            payload.get("final_response"),
        )
        return payload

    except Exception as exc:
        logger.exception("main.chat.exception session_id=%s error=%s", session_id, exc)
        return {
            "session_id": session_id,
            "final_response": "일시적인 오류가 발생했어요. 잠시 후 다시 시도해주세요.",
            "intent": "unknown",
            "next_action": "finish",
            "system_state": "idle",
            "open_callback_flow": False,
            "open_vision_modal": False,
            "message": {
                "type": "ai",
                "content": "일시적인 오류가 발생했어요. 잠시 후 다시 시도해주세요.",
                "structuredData": {
                    "type": "structured",
                    "data": {
                        "suggestions": [
                            "잠시 후 다시 시도",
                            "운영시간 문의",
                        ]
                    },
                },
            },
            "error": "internal_error",
        }