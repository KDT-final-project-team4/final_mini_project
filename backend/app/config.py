import os
from dotenv import load_dotenv

# 환경 변수 로드 (.env 파일이 있다면 읽어옵니다)
load_dotenv()

class Config:
    # LLM 설정
    # .env에 LLM_MODEL이 지정되어 있으면 그걸 쓰고, 없으면 기본값 'gpt-4o-mini' 사용
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
    
    # 온도 설정 (의도 파악용: 정확하고 일관되게)
    ROUTER_TEMPERATURE = 0.0
    
    # 온도 설정 (응답 생성용: 사람처럼 자연스럽게)
    RESPONSE_TEMPERATURE = 0.7