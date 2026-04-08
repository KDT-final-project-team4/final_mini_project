from pathlib import Path
import shutil

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from app.config import (
    EMBEDDING_MODEL,
    CHROMA_COLLECTION_NAME,
    CHROMA_PERSIST_DIRECTORY,
)
from dotenv import load_dotenv
load_dotenv()


BASE_DIR = Path(__file__).resolve().parents[2]   # backend/
FAQ_FILE_PATH = BASE_DIR / "data" / "faq_docs" / "faq.txt"
CHROMA_DIR = BASE_DIR / CHROMA_PERSIST_DIRECTORY

def load_faq_text(file_path: Path) -> str:
    if not file_path.exists():
        raise FileNotFoundError(f'FAQ 파일을 찾을 수 없습니다: {file_path}')
    
    text = file_path.read_text(encoding='utf-8').strip()
    if not text:
        raise ValueError(f'FAQ 파일이 비어 있습니다: {file_path}')
    
    return text

def spli_into_paragraph_chunks(text: str) -> list[Document]:
    """
    현재 faq.txt 구조가 문단 단위 정보 나열형이므로
    빈 줄 기준으로 나눠서 chunk 생성
    """
    raw_chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]

    documents: list[Document] = []
    for idx, chunk in enumerate(raw_chunks):
        documents.append(
            Document(
                page_content=chunk,
                metadata={
                    'source': 'faq.txt',
                    'chunk_index': idx,
                    'type': 'faq',
                },
            )
        )
    
    return documents

def build_vector_db(reset: bool = True) -> None:
    text = load_faq_text(FAQ_FILE_PATH)
    documents = spli_into_paragraph_chunks(text)

    if reset and CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=CHROMA_COLLECTION_NAME,
        persist_directory=str(CHROMA_DIR),
    )

    print("=== Vector DB 생성 완료 ===")
    print(f"FAQ file: {FAQ_FILE_PATH}")
    print(f"Chunks: {len(documents)}")
    print(f"Collection: {CHROMA_COLLECTION_NAME}")
    print(f"Persist dir: {CHROMA_DIR}")


if __name__ == "__main__":
    build_vector_db()