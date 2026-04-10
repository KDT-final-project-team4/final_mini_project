from __future__ import annotations

from typing import Any, Literal, TypedDict


IntentType = Literal["faq", "callback", "vision", "unknown"]
NextActionType = Literal[
    "run_faq",
    "ask_name",
    "ask_phone",
    "run_callback",
    "run_vision",
    "finish",
]
ActiveFlowType = Literal["callback"]
AwaitingFieldType = Literal["name", "phone"]


class CallFlowState(TypedDict, total=False):
    session_id: str
    user_input: str

    intent: IntentType | None
    next_action: NextActionType | None

    active_flow: ActiveFlowType | None
    awaiting_field: AwaitingFieldType | None

    collected_name: str | None
    collected_phone: str | None

    tool_result: dict[str, Any] | None
    final_response: str | None


# graph.py 호환용 별칭
AppState = CallFlowState


def make_initial_state(session_id: str, message: str = "") -> CallFlowState:
    return {
        "session_id": session_id,
        "user_input": message,
        "intent": None,
        "next_action": None,
        "active_flow": None,
        "awaiting_field": None,
        "collected_name": None,
        "collected_phone": None,
        "tool_result": None,
        "final_response": None,
    }


def reset_callback_state(state: CallFlowState) -> CallFlowState:
    state["active_flow"] = None
    state["awaiting_field"] = None
    state["collected_name"] = None
    state["collected_phone"] = None
    return state
'''
state.py 역할
- LangGraph에서 공유하는 상태 스키마 정의
- 각 node가 이 state를 입력받아 읽고 수정함
- graph 실행 중 state가 계속 다음 node로 전달됨

필드 역할
- session_id: 사용자 세션 식별값
- user_input: 현재 사용자 입력
- intent: 요청 종류(faq/callback/unknown)
- next_action: 다음에 실행할 행동
- active_flow: 현재 진행 중인 대화 흐름
- awaiting_field: callback에서 현재 수집 중인 값(name/phone)
- collected_name: 수집한 이름
- collected_phone: 수집한 전화번호
- tool_result: tool 실행 결과
- final_response: 최종 사용자 응답
'''