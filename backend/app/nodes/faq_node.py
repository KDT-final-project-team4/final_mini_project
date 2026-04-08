# faq_node node
from app.state import CallFlowState
from app.tools.faq_tool import faq_tool

def run(state: CallFlowState) -> CallFlowState:
    """
    FAQ tool 실행
    """
    user_input = state.get('user_input', '')
    result = faq_tool(user_input)

    state['tool_result'] = result
    return state
