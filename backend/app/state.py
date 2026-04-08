from typing import Optional, TypedDict, Literal

IntentType = Literal['faq', 'callback', 'unknown']
ActionType = Literal[
    'call_faq',
    'ask_name',
    'ask_phone',
    'call_callback',
    'trigger_vision',
    'respond',
]
FlowType = Literal['callback']

class CallFlowState(TypedDict, total=False):
    # 현재 사용자 입력
    user_input: str

    # 분류된 의도
    intent: Optional[str]

    # Dialogue Manager가 정한 다음 행동
    next_action: Optional[str]

    # 콜백 플로우에서 수집되는 정보
    collected_name: Optional[str]
    collected_phone: Optional[str]

    # tool 실행 결과
    tool_result: Optional[str]

    # 최종 사용자 응답
    final_response: Optional[str]

    # 현재 진행 중인 흐름 기억
    active_flow: Optional[FlowType]
