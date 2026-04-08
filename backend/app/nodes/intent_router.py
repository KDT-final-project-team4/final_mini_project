from app.state import State
# LLM을 사용하기 위한 LangChain 모듈 (예: ChatOpenAI)
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

def intent_router_node(state: State) -> dict:
    user_input = state["user_input"]
    
    # LLM 초기화 (온도를 0으로 설정해 창의성보다는 정확성 우선)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    prompt = PromptTemplate.from_template(
        """너는 고객 센터의 의도 분류기야. 
        사용자의 입력을 보고 다음 3가지 중 하나만 정확히 답변해. 다른 말은 절대 하지 마.
        
        1. '운영시간', '시간', '언제' 등 단순 정보 질문 -> faq
        2. '상담원', '연결', '전화' 등 사람의 도움이 필요한 경우 -> callback
        3. '이상해요', '고장', '사진' 등 텍스트로 파악하기 힘든 상황 -> unknown
        
        사용자 입력: {user_input}
        의도:"""
    )
    
    chain = prompt | llm
    result = chain.invoke({"user_input": user_input})
    
    # LLM의 응답을 소문자로 정리해서 intent 상태 업데이트
    intent = result.content.strip().lower()
    
    # 만약 LLM이 이상한 답을 내놓으면 기본값으로 unknown 처리 (안전장치)
    if intent not in ["faq", "callback", "unknown"]:
        intent = "unknown"
        
    return {"intent": intent}