from app.state import State
from app.tools.faq_tool import faq_tool
from app.tools.callback_tool import callback_tool
from app.tools.vision_tool import vision_tool

def response_node(state: State) -> dict:
    next_action = state.get("next_action")
    
    final_response = ""
    
    # Dialogue Manager가 정해준 방향에 따라 행동 실행 및 응답 생성
    if next_action == "ask_name":
        final_response = "상담원 연결을 위해 고객님의 성함을 입력해주세요."
    elif next_action == "ask_phone":
        final_response = "감사합니다. 연락 받으실 전화번호를 입력해주세요."
    elif next_action == "use_faq_tool":
        final_response = faq_tool(state["user_input"])
    elif next_action == "use_callback_tool":
        # 이름과 전화번호가 있다고 확신할 수 있는 상태
        final_response = callback_tool(state["collected_name"], state["collected_phone"])
    elif next_action == "use_vision_tool":
        final_response = vision_tool()
    
    return {"final_response": final_response}