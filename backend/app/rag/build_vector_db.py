from __future__ import annotations
from typing import Iterable
from pathlib import Path
import shutil

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader

from app.config import (
    EMBEDDING_MODEL,
    CHROMA_COLLECTION_NAME,
    CHROMA_PERSIST_DIRECTORY,
)
from dotenv import load_dotenv
load_dotenv()


BASE_DIR = Path(__file__).resolve().parents[2]   # backend/
LEGACY_FAQ_FILE_PATH = BASE_DIR / "data" / "faq_docs" / "faq.txt"

# 새 PDF/TXT 문서 적재 폴더
KNOWLEDGE_DOCS_DIR = BASE_DIR / "data" / "knowledge_docs"
SUPPORTED_EXTENSIONS = {".pdf", ".txt"}

CHROMA_DIR = BASE_DIR / CHROMA_PERSIST_DIRECTORY

def ensure_knowledge_dir() -> None:
    """
    knowledge_docs 폴더가 없으면 생성
    """
    KNOWLEDGE_DOCS_DIR.mkdir(parents=True, exist_ok=True)

def discover_source_files() -> list[Path]:
    """
    ingestion 대상 파일 탐색

    우선 순위:
    1) data/knowledge_docs 아래의 pdf/txt
    2) 없으면 기존 faq.txt 사용 (하위 호환)
    """
    ensure_knowledge_dir()

    files = [
        path
        for path in KNOWLEDGE_DOCS_DIR.rglob('*')
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    if files:
        return sorted(files)
    
    if LEGACY_FAQ_FILE_PATH.exists():
        return [LEGACY_FAQ_FILE_PATH]
    
    raise FileNotFoundError(
        'ingestion 대상 문서를 찾을 수 없습니다.\n'
        f"- PDF/TXT를 넣을 폴더: {KNOWLEDGE_DOCS_DIR}\n"
        f"- 또는 기존 FAQ 파일: {LEGACY_FAQ_FILE_PATH}"
    )

def load_pdf(file_path: Path) -> list[Document]:
    """
    PDF 로드:
    - 페이지 단위 문서 리스트 반환
    - 이후 chunk splitter가 세부 chunk 생성
    """
    loader = PyPDFLoader(str(file_path))
    pages = loader.load()

    docs: list[Document] = []
    for page_idx, page_doc in enumerate(pages):
        content = (page_doc.page_content or '').strip()
        if not content:
             continue
        
        docs.append(
            Document(
                page_content=content,
                metadata={
                    "source": str(file_path),
                    "file_name": file_path.name,
                    "file_type": "pdf",
                    "doc_type": "knowledge",
                    "page": page_doc.metadata.get("page", page_idx),
                },
            )
        )
    return docs

def load_txt(file_path: Path) -> list[Document]:
    """
    TXT 로드:
    - 전체 텍스트를 하나의 Document로 읽고
    - 이후 splitter에서 chunking
    """
    loader = TextLoader(str(file_path), encoding="utf-8")
    docs = loader.load()

    normalized_docs: list[Document] = []
    for doc in docs:
        content = (doc.page_content or "").strip()
        if not content:
            continue

        normalized_docs.append(
            Document(
                page_content=content,
                metadata={
                    "source": str(file_path),
                    "file_name": file_path.name,
                    "file_type": "txt",
                    "doc_type": "knowledge",
                    "page": None,
                },
            )
        )

    return normalized_docs

def load_documents_from_file(file_path: Path) -> list[Document]:
    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        return load_pdf(file_path)

    if suffix == ".txt":
        return load_txt(file_path)

    return []


def load_all_documents(files: Iterable[Path]) -> list[Document]:
    all_docs: list[Document] = []

    for file_path in files:
        loaded = load_documents_from_file(file_path)
        all_docs.extend(loaded)

    if not all_docs:
        raise ValueError("문서는 발견했지만 실제로 로드된 내용이 없습니다.")

    return all_docs

def split_documents(documents: list[Document]) -> list[Document]:
    """
    실무형 chunking 기준:
    - 너무 짧은 FAQ/안내문부터
    - PDF 문단형 문서까지 무난하게 처리
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=120,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    split_docs = splitter.split_documents(documents)

    enriched_docs: list[Document] = []
    for idx, doc in enumerate(split_docs):
        metadata = dict(doc.metadata)
        metadata["chunk_index"] = idx

        enriched_docs.append(
            Document(
                page_content=doc.page_content.strip(),
                metadata=metadata,
            )
        )

    return enriched_docs

def reset_chroma_dir() -> None:
    if CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)


def build_vector_db(reset: bool = True) -> None:
    source_files = discover_source_files()
    raw_documents = load_all_documents(source_files)
    chunked_documents = split_documents(raw_documents)

    if reset:
        reset_chroma_dir()
    else:
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    Chroma.from_documents(
        documents=chunked_documents,
        embedding=embeddings,
        collection_name=CHROMA_COLLECTION_NAME,
        persist_directory=str(CHROMA_DIR),
    )

    print("=== Vector DB 생성 완료 ===")
    print(f"Collection: {CHROMA_COLLECTION_NAME}")
    print(f"Persist dir: {CHROMA_DIR}")
    print(f"Loaded files: {len(source_files)}")
    print(f"Raw documents: {len(raw_documents)}")
    print(f"Chunks: {len(chunked_documents)}")
    print("Source files:")
    for file_path in source_files:
        print(f" - {file_path}")


if __name__ == "__main__":
    build_vector_db(reset=True)