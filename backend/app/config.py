# --- RAG / Chroma (인덱싱 data/save.py 와 검색 faq_tool 에서 동일하게 사용) ---

# 영문 중심 MiniLM보다 한국어 질의-문서 정렬에 유리한 경우가 많습니다.
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# MMR: 후보를 넉넉히 뽑고(fetch_k), 겹치는 주제만 연속으로 나오는 현상을 줄입니다.
FETCH_K = 28
MMR_K = 5
MMR_LAMBDA = 0.55

# FAQ 답변 생성 (OpenAI, 가벼운 모델)
FAQ_LLM_MODEL = "gpt-4o-mini"
