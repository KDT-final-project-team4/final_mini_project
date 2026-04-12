import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import MarkdownTextSplitter # 마크다운 전용 스플리터로 변경!
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

def initialize_vector_db():
    print("1. 마크다운 문서 불러오는 중...")
    # 경로를 실제 faq_data.md 파일이 있는 곳으로 맞춰주세요!
    loader = TextLoader("C:\\ahy\\final_mini_project\\AI_Call_Service_FAQ_v1.0.md", encoding="utf-8")
    documents = loader.load()

    print("2. 문서 청킹(Chunking) 중...")
    # 마크다운 헤더(##, ###)를 기준으로 잘라주면 검색 품질이 훨씬 좋아집니다.
    text_splitter = MarkdownTextSplitter(chunk_size=300, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)

    print("3. 임베딩 및 Chroma DB 저장 중...")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # ./chroma_db 폴더에 벡터 데이터를 물리적으로 저장
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    print("✅ Vector DB 구축 완료! (백엔드 폴더 안에 chroma_db 폴더 생성됨)")

if __name__ == "__main__":
    initialize_vector_db()