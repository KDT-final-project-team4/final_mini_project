from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from app.graph import build_graph
from app.tools.dialogue_tool import router as twilio_voice_router

app = FastAPI()

app.include_router(twilio_voice_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    collected_name: str | None = None
    collected_phone: str | None = None


@app.post("/chat")
def chat(req: ChatRequest):

    compiled_graph = build_graph()

    initial_state = {
        "user_input": req.message,
        "intent": None,
        "next_action": None,
        "collected_name": req.collected_name,
        "collected_phone": req.collected_phone,
        "tool_result": None,
        "final_response": None,
    }

    final_state = compiled_graph.invoke(initial_state)
    return {"response": final_state.get("final_response", "")}
