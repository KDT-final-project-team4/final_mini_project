# dialogue_manager node
from app.state import CallFlowState

def run(state: CallFlowState) -> CallFlowState:
    """
    현재 state를 보고 다음 행동(next_action)을 결정
    """
    intent = state.get('intent')
    name = state.get('collected_name')
    phone = state.get('collected_phone')

    if intent == 'faq':
        state['next_action'] = 'call_faq'
        state['active_flow'] = None
        return state
    
    if intent == 'callback':
        state['active_flow'] = 'callback'

        if not name:
            state['next_action'] = 'ask_name'
            return state
        if not phone:
            state['next_action'] = 'ask_phone'
            return state
        
        state['next_action'] = 'call_callback'
        return state
    
    state['next_action'] = 'trigger_vision'
    state['active_flow'] = None

    print("[Dialogue Manager] intent:", intent)
    print("[Dialogue Manager] next_action:", state.get("next_action"))
    print("[Dialogue Manager] state:", state)

    return state