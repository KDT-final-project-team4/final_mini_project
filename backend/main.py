from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from app.graph import app as langgraph_app

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. 프론트엔드에서 메세지와 함께 '현재 상태'도 보내도록 모델 수정
class ChatRequest(BaseModel):
    message: str
    state: dict = {}  # 프론트가 보내줄 기억 장치

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    # 2. 전역 변수 제거! 프론트에서 받은 상태를 그대로 가져옵니다.
    current_state = req.state
    
    # 처음 대화를 시작해서 상태가 비어있다면 기본 틀을 만들어줍니다.
    if not current_state:
        current_state = {
            "user_input": "",
            "intent": None,
            "next_action": None,
            "collected_name": None,
            "collected_phone": None,
            "tool_result": None,
            "final_response": None
        }
    
    # 3. 새로운 메시지 입력 및 슬롯 필링
    current_state["user_input"] = req.message
    
    if current_state.get("next_action") == "ask_name":
        current_state["collected_name"] = req.message
    elif current_state.get("next_action") == "ask_phone":
        current_state["collected_phone"] = req.message

    # 🌟 [로그 추가 1] LangGraph 들어가기 직전의 상태 출력
    print(f"\n{'='*50}")
    print(f"🗣️ [사용자 입력]: {req.message}")
    print(f"🔍 [그래프 진입 전 State]: {current_state}")

    # 4. LangGraph 실행 (프론트가 준 기억을 바탕으로 판단)
    new_state = langgraph_app.invoke(current_state)

    # 🌟 [로그 추가 2] LangGraph 실행 완료 후의 상태 출력
    print(f"✨ [그래프 실행 후 State]: {new_state}")
    print(f"🤖 [최종 응답]: {new_state['final_response']}")
    print(f"{'='*50}\n")
    
    # 5. [중요] 응답 메시지와 함께 '업데이트된 기억(new_state)'을 프론트에게 다시 돌려줌!
    return {
        "response": new_state["final_response"],
        "state": new_state 
    }