import os
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# =================================================================
# 🌟 [성능 최적화] 서버가 켜질 때 딱 한 번만 DB를 메모리에 로드합니다.
# =================================================================
current_dir = os.path.dirname(__file__) 
db_path = os.path.abspath(os.path.join(current_dir, "../../chroma_db"))

print(f"\n🚀 [FAQ Tool 초기화] Chroma DB 연결 중... (최초 1회 실행)")

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
# 전역 변수로 vectorstore를 미리 만들어 둡니다.
vectorstore = Chroma(persist_directory=db_path, embedding_function=embeddings)

print("✅ [FAQ Tool 초기화] DB 로드 완료! 언제든 검색할 준비가 되었습니다.\n")
# =================================================================


def faq_tool(query: str) -> str:
    print(f"\n🔍 [FAQ 검색 시작] 질문: {query}")
    
    # 함수 안에서는 이미 로드된 vectorstore를 냅다 쓰기만 합니다! (속도 폭발 🚀)
    docs = vectorstore.similarity_search(query, k=2)
    
    print(f"🧐 [RAG 디버깅] 찾은 문서 개수: {len(docs)}개")
    
    # 문서가 없는 경우 방어
    if not docs:
        print("🚨 [RAG 디버깅] 문서를 하나도 못 찾았습니다. DB가 비어있거나 경로가 틀렸습니다.")
        return "관련된 정보를 찾을 수 없습니다."
        
    # 찾은 문서 합치기
    result = "\n".join([doc.page_content for doc in docs])
    
    print(f"📄 [RAG 디버깅] LLM에게 던져줄 지식 데이터:\n{result}\n")
    
    return result