from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from app.config import (
    EMBEDDING_MODEL,
    CHROMA_COLLECTION_NAME,
    CHROMA_PERSIST_DIRECTORY,
)

# 🔹 Vector DB 로드 (서버 시작 시 1회 생성)
_embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

_vectorstore = Chroma(
    collection_name=CHROMA_COLLECTION_NAME,
    persist_directory=CHROMA_PERSIST_DIRECTORY,
    embedding_function=_embeddings,
)

def faq_tool(query: str) -> str:
    """
    RAG 기반 FAQ 검색
    """
    try:
        docs = _vectorstore.similarity_search(query, k=2)

        if not docs:
            return '해당 질문에 대한 답변을 찾지 못했습니다.'
        
        # 가장 유사한 문서 사용
        best_doc = docs[0].page_content

        return best_doc
    
    except Exception as e:
        print(f'[FAQ TOOL ERROR] {e}')
        return '죄송합니다. 현재 FAQ 조회 중 문제가 발생했습니다.'