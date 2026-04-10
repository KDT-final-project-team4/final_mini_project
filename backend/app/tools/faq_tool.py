from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from pathlib import Path

_CHROMA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "chroma_db"


def save_to_chroma_db(md_path: str):
    with open(md_path, "r", encoding="utf-8") as file:
        md_content = file.read()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["#", "##", "###", "---"],
        length_function=len,
    )

    print("문서 분할 중...")
    docs = text_splitter.split_documents([Document(page_content=md_content)])
    print("문서 분할 완료")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print("Chroma DB 저장 중...")
    _CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    Chroma.from_documents(
        docs,
        embeddings,
        persist_directory=str(_CHROMA_DIR),
    )
    print("Chroma DB 저장 완료")


# 최초 한 번만 실행(embedding 저장용)
# save_to_chroma_db("backend/data/faq.md")


# chroma db search -> response
def faq_tool(query: str):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    db = Chroma(persist_directory=_CHROMA_DIR, embedding_function=embeddings)
    results = db.similarity_search(query)
    return (
        results[0].page_content
        if results
        else "해당 질문에 대한 답변을 찾을 수 없습니다."
    )
