from typing import Optional, TypedDict

class CallFlowState(TypedDict):
    user_input: str
    intent: Optional[str]
    next_action: Optional[str]
    collected_name: Optional[str]
    collected_phone: Optional[str]
    tool_result: Optional[str]
    final_response: Optional[str]