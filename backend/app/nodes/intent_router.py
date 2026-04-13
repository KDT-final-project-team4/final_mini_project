import re
from typing import Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from app.config import FAQ_LLM_MODEL
from app.prompts.intent_router_prompt import get_intent_prompt


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

    # ChatGoogleGenerativeAI(Gemini)에 gpt-4o-mini 같은 OpenAI 모델명을 넣으면 API 오류가 납니다.
    llm = ChatOpenAI(
        model=FAQ_LLM_MODEL,
        temperature=0,
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
