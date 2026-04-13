from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI

from app.config import CHROMA_COLLECTION, CHROMA_DIR, EMBED_MODEL, OPENAI_LLM_MODEL

_faq_db: Chroma | None = None
_chat_llm: ChatOpenAI | None = None


def init_runtime() -> None:
    global _faq_db, _chat_llm
    if _chat_llm is None:
        _chat_llm = ChatOpenAI(model=OPENAI_LLM_MODEL, temperature=0, max_retries=2)
    if _faq_db is None:
        embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
        _faq_db = Chroma(
            persist_directory=str(CHROMA_DIR),
            embedding_function=embeddings,
            collection_name=CHROMA_COLLECTION,
        )


def get_chat_llm() -> ChatOpenAI:
    if _chat_llm is None:
        raise RuntimeError("Runtime not initialized. Call init_runtime() at app startup.")
    return _chat_llm


def get_faq_db() -> Chroma:
    if _faq_db is None:
        raise RuntimeError("Runtime not initialized. Call init_runtime() at app startup.")
    return _faq_db
