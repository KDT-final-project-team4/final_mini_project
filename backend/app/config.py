from pathlib import Path

# --- Paths ---
BACKEND_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_ROOT / "data"
CHROMA_DIR = DATA_DIR / "chroma_db"

# --- RAG / Chroma ---
CHROMA_COLLECTION = "pdf_documents"
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
FETCH_K = 28
MMR_K = 5
MMR_LAMBDA = 0.55
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100
CHUNK_SEPARATORS = ["\n\n", " ", ""]

# --- LLM ---
OPENAI_LLM_MODEL = "gpt-4o-mini"
# 하위 호환: 기존 코드에서 사용하는 이름 유지
FAQ_LLM_MODEL = OPENAI_LLM_MODEL

# --- Voice / STT ---
DIALOGUE_SYSTEM_PROMPT = """
당신은 매우 유능하고 똑똑한 상담원입니다.
사용자의 질문에 너무 장황하지 않게만 대답해 주세요.

현재 들어온 질문만으로 대답을 생성해 내는 것이 어렵다면
이전 질문들을 참고하여 대답을 생성해 내세요.

사용자 질문:
{user_speech}

이전 질문들:
{previous_speech_data}
"""
DEEPGRAM_MODEL = "nova-2"
DEEPGRAM_LANGUAGE = "ko"
DEEPGRAM_ENCODING = "mulaw"
DEEPGRAM_SAMPLE_RATE = 8000
DEEPGRAM_CHANNELS = 1
