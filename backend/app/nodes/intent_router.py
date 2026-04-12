from app.state import State
# LLM을 사용하기 위한 LangChain 모듈 (예: ChatOpenAI)
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from app.config import Config

def intent_router_node(state: State) -> dict:
    user_input = state["user_input"]
    next_action = state.get("next_action") # 이전 상태의 next_action을 가져옴
    
    # [핵심 추가 코드] 이미 콜백 진행 중(이름이나 전화번호를 묻는 중)이라면,
    # 의도를 다시 파악할 필요 없이 무조건 'callback'으로 유지합니다.
    if next_action in ["ask_name", "ask_phone"]:
        return {"intent": "callback"}
    
    # 🌟 [수정] 하드코딩된 값을 Config 변수로 교체!
    llm = ChatOpenAI(
        model=Config.LLM_MODEL, 
        temperature=Config.ROUTER_TEMPERATURE
    )
    
    prompt = PromptTemplate.from_template(
        """너는 고객 센터의 의도 분류기야. 
        사용자의 입력을 보고 다음 3가지 중 하나만 정확히 답변해. 다른 말은 절대 하지 마.
        
        1. 단순 정보성 질문 및 서비스에 대한 모든 문의 사항 -> faq
            (포함되는 주제: AI 서비스 정의, 도입 방식(클라우드/구축형), 다국어 지원, CRM/API 연동, STT 인식률, 시나리오 관리, 운영 시간 설정, 감정 분석, 장애 대응(서버다운 등), 녹취 보관, 스팸 차단, 업종별 특화(예약/배송/인증), 동시 접속 제한, 리포트 제공, 도입 테스트(PoC), 유지보수, 요금 등. 
            🚨주의: "상담원 연결은 어떻게 되나요?"나 "상담원이 개입할 수 있나요?" 처럼 '기능에 대한 단순 질문'도 faq로 분류할 것.)

        2. 실제 사람 상담원과의 통화나 연락을 직접적으로 요청하는 경우 -> callback
            (예: "상담원 연결해줘", "사람이랑 통화할래", "담당자 전화 부탁해", "콜백 남겨줘" 등. 실제 연락처 수집이 필요한 상황)

        3. '이상해요', '고장', '파손', '불량' 등 반드시 눈으로 사진이나 현장 상황을 봐야만 파악할 수 있는 문제 -> unknown
        
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