from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    return {
        "response": f"받은 메시지: {req.message}",
        "intent": "mock",
        "next_action": "mock"
    }
