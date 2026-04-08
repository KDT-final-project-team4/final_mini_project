from fastapi import FastAPI
from pydantic import BaseModel
from app.nodes import intent_router
from fastapi.middleware.cors import CORSMiddleware
from app.graph import build_graph

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],  
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(req: ChatRequest):

    app = build_graph()

    initial_state = {
        "user_input": req.message,
        "intent": None,
        "next_action": None,
        "collected_name": None,
        "collected_phone": None,
        "tool_result": None,
        "final_response": None
    }

    final_state = app.invoke(initial_state)
    return {"response": final_state.get('final_response', '')}
