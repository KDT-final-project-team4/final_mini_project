import os
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

def faq_tool(query: str) -> str:
    # 1. 헷갈리지 않게 DB 위치를 '절대 경로'로 쾅 박아줍니다.
    current_dir = os.path.dirname(__file__) # 현재 파일(faq_tool.py)의 위치
    db_path = os.path.abspath(os.path.join(current_dir, "../../chroma_db"))
    
    print(f"\n📂 [RAG 디버깅] DB 찾는 경로: {db_path}")
    
    # 2. DB 연결
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma(persist_directory=db_path, embedding_function=embeddings)
    
    # 3. 유사 문서 검색
    docs = vectorstore.similarity_search(query, k=2)
    
    print(f"🧐 [RAG 디버깅] 찾은 문서 개수: {len(docs)}개")
    
    # 4. 문서가 없는 경우 방어
    if not docs:
        print("🚨 [RAG 디버깅] 헉! 문서를 하나도 못 찾았습니다. DB가 비어있거나 경로가 틀렸습니다.")
        return "관련된 정보를 찾을 수 없습니다."
        
    # 5. 찾은 문서 합치기
    result = "\n".join([doc.page_content for doc in docs])
    
    print(f"📄 [RAG 디버깅] LLM에게 던져줄 지식 데이터:\n{result}\n")
    
    return result