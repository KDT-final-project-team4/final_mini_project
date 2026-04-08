from fastapi import FastAPI
from pydantic import BaseModel
from app.nodes import intent_router
from fastapi.middleware.cors import CORSMiddleware

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
    state = {
        "user_input": req.message,
        "intent": None,
        "next_action": None,
        "collected_name": None,
        "collected_phone": None,
        "tool_result": None,
        "final_response": None
    }

    state = intent_router.run(state)