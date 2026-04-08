# config placeholder

# LLM 설정
INTENT_ROUTER_MODEL = "gpt-4o-mini"
INTENT_ROUTER_TEMPERATURE = 0

RESPONSE_MODEL = "gpt-4o-mini"
RESPONSE_TEMPERATURE = 0.2

# API / 서버 관련
API_TITLE = "CallFlow Mini API"

# 앞으로 RAG 붙일 때 사용할 자리
EMBEDDING_MODEL = "text-embedding-3-small"
CHROMA_COLLECTION_NAME = "callflow_faq"
CHROMA_PERSIST_DIRECTORY = "./data/chroma"