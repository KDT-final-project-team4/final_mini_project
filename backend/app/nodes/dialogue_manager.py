# dialogue_manager node
from app.state import CallFlowState

def run(state: CallFlowState) -> CallFlowState:
    """
    현재 state를 보고 다음 행동을 결정하는 오케스트레이터 역할
    """
    intent = state.get('intent')
    active_flow = state.get("active_flow")
    collected_name = state.get("collected_name")
    collected_phone = state.get("collected_phone")

    next_action = None

    # 1. FAQ → FAQ specialist로 라우팅
    if intent == "faq":
        next_action = "route_faq"
    
    # 2. Callback → 상태 기반 단계 처리
    elif intent == "callback" or active_flow == "callback":
        state["active_flow"] = "callback"
        state["collected_name"] = None
        state["collected_phone"] = None

        if not collected_name:
            next_action = "ask_name"
        elif not collected_phone:
            next_action = "ask_phone"
        else:
            next_action = "route_callback"

    # 3. 비전 필요
    elif intent == "vision_needed":
        next_action = "route_vision"

    # 4. 지원 불가
    else:
        next_action = "route_unsupported"

    state["next_action"] = next_action

    print("[Dialogue Manager]")
    print("  intent:", intent)
    print("  active_flow:", active_flow)
    print("  collected_name:", collected_name)
    print("  collected_phone:", collected_phone)
    print("  next_action:", next_action)

    return state