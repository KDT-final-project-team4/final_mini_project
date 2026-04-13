import re
import sys
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import (
    CHROMA_COLLECTION,
    CHROMA_DIR,
    CHUNK_OVERLAP,
    CHUNK_SEPARATORS,
    CHUNK_SIZE,
    EMBED_MODEL,
)

PDF_DIR = Path(__file__).resolve().parent


def _normalize_pdf_text(text: str) -> str:
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def load_pdf_documents():
    paths = sorted(PDF_DIR.glob("*.pdf"))
    if not paths:
        raise FileNotFoundError(
            f"PDF 파일이 없습니다. 다음 폴더에 .pdf를 넣어 주세요: {PDF_DIR}"
        )
    all_docs = []
    for pdf_path in paths:
        loader = PyMuPDFLoader(str(pdf_path))
        docs = loader.load()
        for d in docs:
            d.page_content = _normalize_pdf_text(d.page_content)
        all_docs.extend(docs)
    return all_docs


def save_pdfs_to_chroma():
    raw_docs = load_pdf_documents()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=CHUNK_SEPARATORS,
    )
    print("문서 분할 중...")
    splits = text_splitter.split_documents(raw_docs)
    print(f"분할 완료: {len(splits)}개 청크")

    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

    print(f"Chroma DB 저장 중... ({CHROMA_DIR})")
    print(f"임베딩 모델: {EMBED_MODEL} (faq_tool과 동일해야 검색이 맞습니다)")
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    Chroma.from_documents(
        splits,
        embeddings,
        persist_directory=str(CHROMA_DIR),
        collection_name=CHROMA_COLLECTION,
    )
    print("Chroma DB 저장 완료")


if __name__ == "__main__":
    save_pdfs_to_chroma()
