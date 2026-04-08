# response_node node
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.state import CallFlowState
from app.prompts.response_prompt import SYSTEM_PROMPT
from app.config import (
    RESPONSE_MODEL,
    RESPONSE_TEMPERATURE,
)

load_dotenv()

llm = ChatOpenAI(
    model=RESPONSE_MODEL,
    temperature=RESPONSE_TEMPERATURE,
)

def run(state: CallFlowState) -> CallFlowState:
    """
    현재 state를 바탕으로 최종 사용자 응답 생성
    """
    action = state.get('next_action')
    tool_result = state.get('tool_result')

    # LLM에 넘길 최소 컨텍스트
    context = {
        "intent": state.get("intent"),
        "next_action": action,
        "tool_result": tool_result,
    }

    response = llm.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=json.dumps(context, ensure_ascii=False)),
        ]
    )

    content = response.content

    try:
        parsed = json.loads(content)
        final_response = parsed.get("response", "요청을 처리하지 못했습니다.")
    except Exception:
        # 파싱 실패 시 fallback
        if action == "ask_name":
            final_response = "이름을 알려주세요."
        elif action == "ask_phone":
            final_response = "전화번호를 알려주세요."
        elif tool_result:
            final_response = tool_result
        else:
            final_response = "요청을 처리하지 못했습니다."

    state["final_response"] = final_response

    print("[Response Node] next_action:", action)
    print("[Response Node] final_response:", state.get("final_response"))

    return state
