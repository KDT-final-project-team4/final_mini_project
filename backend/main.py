"""앱 import보다 먼저 .env를 로드해야 OPENAI_API_KEY 등이 파일 값으로 맞춰집니다."""

from pathlib import Path

from dotenv import load_dotenv

# 시스템 환경 변수에 이미 키가 있으면 기본 load_dotenv는 덮어쓰지 않음 → override=True
load_dotenv(Path(__file__).resolve().parent / ".env", override=True)

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from app.graph import build_graph
from app.tools.dialogue_tool import router as twilio_voice_router

app = FastAPI()

app.include_router(twilio_voice_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    collected_name: str | None = None
    collected_phone: str | None = None


@app.post("/chat")
def chat(req: ChatRequest):

    compiled_graph = build_graph()

    initial_state = {
        "user_input": req.message,
        "intent": None,
        "next_action": None,
        "collected_name": req.collected_name,
        "collected_phone": req.collected_phone,
        "tool_result": None,
        "final_response": None,
    }

    final_state = compiled_graph.invoke(initial_state)
    return {"response": final_state.get("final_response", "")}
