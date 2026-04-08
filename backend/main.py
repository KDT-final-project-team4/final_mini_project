from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.graph import build_graph

app = FastAPI(title='CallFlow Mini API')

# 프론트 연동용 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'], # 나중에 프론트 주소로 제한
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

graph = build_graph()

class SessionState(BaseModel):
    collected_name: Optional[str] = None
    collected_phone: Optional[str] = None
    active_flow: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    session_state: Optional[SessionState] = None

class ChatResponse(BaseModel):
    response: str
    intent: Optional[str] = None
    next_action: Optional[str] = None
    session_state: SessionState

@app.get('/')
def root():
    return {'message': 'CallFlow Mini API is running'}

@app.post('/chat', response_model=ChatResponse)
def chat(req: ChatRequest):
    # 프론트에서 전달된 최소 session state 복원
    collected_name = None
    collected_phone = None
    active_flow = None

    if req.session_state:
        collected_name = req.session_state.collected_name
        collected_phone = req.session_state.collected_phone
        active_flow = req.session_state.active_flow

    state = {
        'user_input': req.message,
        'intent': None,
        'next_action': None,
        "collected_name": collected_name,
        "collected_phone": collected_phone,
        "tool_result": None,
        "final_response": None,
        "active_flow": active_flow,
    }
    
    result = graph.invoke(state)

    return ChatResponse(
        response=result.get("final_response", "응답 생성 실패"),
        intent=result.get("intent"),
        next_action=result.get("next_action"),
        session_state=SessionState(
            collected_name=result.get("collected_name"),
            collected_phone=result.get("collected_phone"),
            active_flow=result.get('active_flow')
        ),
    )
