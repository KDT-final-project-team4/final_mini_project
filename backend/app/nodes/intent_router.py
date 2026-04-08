from app.prompts.intent_router_prompt import get_intent_prompt
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from pydantic import BaseModel, Field
from typing import Optional
import os

"""
    모델명: models/gemini-2.5-flash
모델명: models/gemini-2.5-pro
모델명: models/gemini-2.0-flash
모델명: models/gemini-2.0-flash-001
모델명: models/gemini-2.0-flash-lite-001
모델명: models/gemini-2.0-flash-lite
모델명: models/gemini-2.5-flash-preview-tts
모델명: models/gemini-2.5-pro-preview-tts
모델명: models/gemini-flash-latest
모델명: models/gemini-flash-lite-latest
모델명: models/gemini-pro-latest
모델명: models/gemini-2.5-flash-lite
모델명: models/gemini-2.5-flash-image
모델명: models/gemini-3-pro-preview
모델명: models/gemini-3-flash-preview
모델명: models/gemini-3.1-pro-preview
모델명: models/gemini-3.1-pro-preview-customtools
모델명: models/gemini-3.1-flash-lite-preview
모델명: models/gemini-3-pro-image-preview
모델명: models/gemini-3.1-flash-image-preview
모델명: models/gemini-robotics-er-1.5-preview
모델명: models/gemini-2.5-computer-use-preview-10-2025
    """

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# state 업데이트를 위해 structure 클래스 정의
class RouterOutput(BaseModel):
    intent: str = Field(description="유저의 의도 (예: callback, faq, vision, dialogue)")
    next_action: str = Field(description="다음에 수행할 작업 (예: CALLBACK_NODE, FAQ_NODE, VISION_NODE, DIALOGUE_NODE)")
    reason: str = Field(description="이 의도로 판단한 이유")


# intent_router node
def run(state):
    user_input = state.get('user_input')

    llm = ChatGoogleGenerativeAI(
        model='gemini-2.5-flash',
        temperature=0.3,
        max_tokens=None,
        timeout=None,
        max_retries=2
    )

    # 사용자 질문 의도 판단 후 state 업데이트
    structured_llm = llm.with_structured_output(RouterOutput)

    prompt = get_intent_prompt()
    prompt_template = ChatPromptTemplate.from_template(prompt)

    chain = prompt_template | structured_llm 

    response = chain.invoke({
        'user_question': user_input
    })

    print(f"판단된 의도: {response.intent}")
    print(f"판단 이유: {response.reason}")

    # state update
    return {
        'intent': response.intent,
        'next_action': response.next_action
    }
