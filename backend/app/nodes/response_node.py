# response_node node
from app.state import CallFlowState

def run(state: CallFlowState) -> CallFlowState:
    """
    최종 사용자 응답 생성
    """
    action = state.get('next_action')
    tool_result = state.get('tool_result')

    if action == 'ask_name':
        state['final_response'] = '이름을 알려주세요.'
        return state
    
    if action == 'ask_phone':
        state['final_response'] = '전화번호를 알려주세요.'
        return state
    
    if action in ['call_faq', 'call_callback', 'trigger_vision']:
        state['final_response'] = tool_result
        return state
    
    state['final_response'] = '요청을 처리하지 못했습니다.'
    return state
