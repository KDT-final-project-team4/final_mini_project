# callback_node node
from app.state import CallFlowState
from app.tools.callback_tool import callback_tool

def run(state: CallFlowState) -> CallFlowState:
    """
    Callback Specialist Agent Node
    - 수집된 이름/전화번호를 바탕으로 callback_tool 실행
    - 실행 결과를 tool_result에 저장
    - callback flow 종료
    """
    name = state.get('collected_name')
    phone = state.get('collected_phone')
    
    result = callback_tool(name, phone)

    state['tool_result'] = result
    state['active_flow'] = None

    print('[Callback Node]')
    print(' collected_name:', name)
    print(' collected_phone:', phone)
    print(' tool_result:', result)
    print(' active_flow:', state.get('active_flow'))

    return state
