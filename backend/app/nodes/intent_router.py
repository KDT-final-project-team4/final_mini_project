# intent_router node
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.state import CallFlowState
from app.prompts.intent_router_prompt import SYSTEM_PROMPT
from app.config import (
    INTENT_ROUTER_MODEL,
    INTENT_ROUTER_TEMPERATURE,
)

load_dotenv()

llm = ChatOpenAI(
    model=INTENT_ROUTER_MODEL,
    temperature=INTENT_ROUTER_TEMPERATURE,
)

def run(state: CallFlowState) -> CallFlowState:
    """
    사용자 입력을 faq / callback / unknown 으로 분류
    단, 이미 callback 흐름이 진행 중이면 intent를 유지
    """
    active_flow = state.get('active_flow')
    user_input = state.get('user_input', '').strip()

    if active_flow == 'callback':
        state['intent'] = 'callback'
        return state

    response = llm.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_input),
        ]
    )

    content = response.content

    try:
        parsed = json.loads(content)
        intent = parsed.get("intent", "unknown")
    except Exception:
        intent = "unknown"

    if intent not in ["faq", "callback", "unknown"]:
        intent = "unknown"

    state["intent"] = intent

    print("[Intent Router] user_input:", user_input)
    print("[Intent Router] intent:", state.get("intent"))

    return state
