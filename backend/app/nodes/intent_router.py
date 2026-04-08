# intent_router node
from app.state import CallFlowState

def run(state: CallFlowState) -> CallFlowState:
    """
    사용자 입력을 faq / callback / unknown 으로 분류
    지금은 rule-based로 먼저 구현
    """
    user_input = state.get('user_input', '').strip().lower()

    if any(keyword in user_input for keyword in ['운영시간', '주차', '반품', '진료시간']):
        state['intent'] = 'faq'
    elif any(keyword in user_input for keyword in ['상담원', '연락', '콜백', '전화']):
        state['intent'] = 'callback'
    else:
        state['intent'] = 'unknown'
    
    return state
