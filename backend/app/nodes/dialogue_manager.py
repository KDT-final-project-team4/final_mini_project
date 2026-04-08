from app.state import State

def dialogue_manager_node(state: State) -> dict:
    intent = state.get("intent")
    name = state.get("collected_name")
    phone = state.get("collected_phone")
    
    # 1. FAQ 인 경우
    if intent == "faq":
        return {"next_action": "use_faq_tool"}
        
    # 2. Vision(Unknown) 인 경우
    elif intent == "unknown":
        return {"next_action": "use_vision_tool"}
        
    # 3. Callback 인 경우 (Slot Filling 로직)
    elif intent == "callback":
        # 이름이 비어있다면? -> 이름부터 물어보라고 지시
        if not name:
            return {"next_action": "ask_name"}
        # 이름은 있는데 전화번호가 비어있다면? -> 전화번호를 물어보라고 지시
        elif not phone:
            return {"next_action": "ask_phone"}
        # 둘 다 수집되었다면? -> 콜백 등록 툴 실행 지시
        else:
            return {"next_action": "use_callback_tool"}
            
    # 예외 처리
    return {"next_action": "end"}