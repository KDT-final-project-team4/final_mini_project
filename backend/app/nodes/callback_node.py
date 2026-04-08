# callback_node node
from app.state import CallFlowState
from app.tools.callback_tool import callback_tool

def run(state: CallFlowState) -> CallFlowState:
    """
    Callback tool 실행
    """
    name = state.get('collected_name', '')
    phone = state.get('collected_phone', '')
    
    result = callback_tool(name, phone)

    state['tool_result'] = result
    state['active_flow'] = None
    return state
