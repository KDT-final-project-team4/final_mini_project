from app.state import State
from app.tools.faq_tool import faq_tool
from app.tools.callback_tool import callback_tool
from app.tools.vision_tool import vision_tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from app.config import Config

def response_node(state: State) -> dict:
    next_action = state.get("next_action")
    user_input = state.get("user_input")
    
    # 1. 툴 실행 및 시스템의 '목적(Raw Data)'만 먼저 정의합니다.
    raw_info = ""
    if next_action == "ask_name":
        raw_info = "시스템 지시: 고객에게 콜백 예약을 위해 '이름'을 정중하게 물어보세요."
    elif next_action == "ask_phone":
        raw_info = "시스템 지시: 고객에게 콜백 예약을 위해 '전화번호'를 물어보세요."
    elif next_action == "use_faq_tool":
        # 나중에는 여기서 진짜 DB 검색 결과가 들어옵니다.
        raw_info = f"FAQ 검색 결과: {faq_tool(user_input)}"
    elif next_action == "use_callback_tool":
        result = callback_tool(state["collected_name"], state["collected_phone"])
        raw_info = f"콜백 등록 결과: {result}"
    elif next_action == "use_vision_tool":
        raw_info = f"시스템 지시: 텍스트로 파악이 어려우니 {vision_tool()}"
        
    # 🌟 [수정] 하드코딩된 값을 Config 변수로 교체!
    llm = ChatOpenAI(
        model=Config.LLM_MODEL, 
        temperature=Config.RESPONSE_TEMPERATURE
    )
    
    prompt = PromptTemplate.from_template(
        """너는 CallFlow AI의 친절하고 전문적인 전화 상담원이야.
        아래에 주어진 '상황/정보'를 바탕으로 고객에게 할 자연스러운 응답을 생성해줘.

        [규칙]
        - 고객의 질문 의도에 공감하거나 자연스럽게 호응할 것.
        - 🌟 '상황/정보'의 내용 중 **고객의 질문과 직접적으로 관련된 답변만** 골라서 할 것.
        - 🌟 고객이 묻지 않은 무관한 정보(TMI)는 절대 언급하지 말 것.
        - 만약 '상황/정보'에 답변할 내용이 없다면, "죄송하지만 해당 내용은 확인이 어렵습니다."라고 할 것.
        - 전화 통화 중이므로 한 번에 너무 길게 말하지 말 것.

        고객의 질문: {user_input}
        상황/정보: {raw_info}

        상담원 응답:"""
    )
    
    chain = prompt | llm
    result = chain.invoke({
        "user_input": user_input,
        "raw_info": raw_info
    })
    
    # 생성된 자연스러운 문장을 최종 응답으로 반환합니다.
    return {"final_response": result.content.strip()}