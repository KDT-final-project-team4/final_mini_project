# vision_node node
from app.state import CallFlowState
from app.tools.vision_tool import vision_tool

def run(state: CallFlowState) -> CallFlowState:
    """
    Vision fallback tool 실행
    """
    result = vision_tool()

    state['tool_result'] = result
    return state
