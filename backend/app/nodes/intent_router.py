from app.prompts.intent_router_prompt import get_intent_prompt
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# Gemini 일일 한도 복구 후 intent를 다시 쓸 때: 아래 import 주석 해제 + llm 블록 교체
# from langchain_google_genai import ChatGoogleGenerativeAI
import re

from pydantic import BaseModel, Field
from typing import Optional
import os

"""
    모델명: models/gemini-2.5-flash
모델명: models/gemini-2.5-pro
모델명: models/gemini-2.0-flash
모델명: models/gemini-2.0-flash-001
모델명: models/gemini-2.0-flash-lite-001
모델명: models/gemini-2.0-flash-lite
모델명: models/gemini-2.5-flash-preview-tts
모델명: models/gemini-2.5-pro-preview-tts
모델명: models/gemini-flash-latest
모델명: models/gemini-flash-lite-latest
모델명: models/gemini-pro-latest
모델명: models/gemini-2.5-flash-lite
모델명: models/gemini-2.5-flash-image
모델명: models/gemini-3-pro-preview
모델명: models/gemini-3-flash-preview
모델명: models/gemini-3.1-pro-preview
모델명: models/gemini-3.1-pro-preview-customtools
모델명: models/gemini-3.1-flash-lite-preview
모델명: models/gemini-3-pro-image-preview
모델명: models/gemini-3.1-flash-image-preview
모델명: models/gemini-robotics-er-1.5-preview
모델명: models/gemini-2.5-computer-use-preview-10-2025
    """

load_dotenv()
# Gemini 재사용 시 ChatGoogleGenerativeAI가 GOOGLE_API_KEY를 읽도록 유지
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY") or ""


def _normalize_phone(raw: str | None) -> str | None:
    if not raw:
        return None
    d = re.sub(r"\D", "", raw.strip())
    if len(d) in (10, 11) and d.startswith("01"):
        return d
    return None


# state 업데이트를 위해 structure 클래스 정의 (with_structured_output → response 필드로 접근)
class RouterOutput(BaseModel):
    intent: str = Field(description="유저의 의도 (예: callback, faq, vision, default)")
    next_action: str = Field(
        description="다음에 수행할 작업 (예: CALLBACK_NODE, FAQ_NODE, VISION_NODE, RESPONSE_NODE)"
    )
    reason: str = Field(description="이 의도로 판단한 이유")
    collected_name: Optional[str] = Field(
        default=None,
        description="이번 유저 발화에서 추출한 이름. 없으면 null",
    )
    collected_phone: Optional[str] = Field(
        default=None,
        description="이번 유저 발화에서 추출한 휴대폰 번호. 없으면 null",
    )


def _merge_slot(prev: str | None, llm_val: str | None) -> str | None:
    v = (llm_val or "").strip()
    if v:
        return v
    return (prev or None) if isinstance(prev, str) and prev.strip() else prev


# intent_router node
def run(state):
    user_input = state.get("user_input")
    session_name = state.get("collected_name")
    session_phone = state.get("collected_phone")
    sn = (
        session_name.strip()
        if isinstance(session_name, str) and session_name.strip()
        else "없음"
    )
    sp = (
        session_phone.strip()
        if isinstance(session_phone, str) and session_phone.strip()
        else "없음"
    )

    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.5-flash",
        temperature=0.3,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    # 사용자 질문 의도 판단 후 state 업데이트
    structured_llm = llm.with_structured_output(RouterOutput)

    prompt = get_intent_prompt(sn, sp)
    prompt_template = ChatPromptTemplate.from_template(prompt)

    chain = prompt_template | structured_llm

    response = chain.invoke({"user_question": user_input})

    print(f"판단된 의도: {response.intent}")
    print(f"판단 이유: {response.reason}")
    print(
        f"추출 이름: {response.collected_name!r}, 추출 전화: {response.collected_phone!r}"
    )

    merged_name = _merge_slot(session_name, response.collected_name)
    merged_phone = _normalize_phone(response.collected_phone) or _normalize_phone(
        session_phone if isinstance(session_phone, str) else None
    )

    return {
        "intent": response.intent,
        "next_action": response.next_action,
        "collected_name": merged_name,
        "collected_phone": merged_phone,
    }
