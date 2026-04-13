from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from app.config import EMBED_MODEL, FETCH_K, MMR_K, MMR_LAMBDA

_CHROMA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "chroma_db"
_CHROMA_COLLECTION = "pdf_documents"


def faq_tool(query: str) -> str:
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    db = Chroma(
        persist_directory=str(_CHROMA_DIR),
        embedding_function=embeddings,
        collection_name=_CHROMA_COLLECTION,
    )
    results = db.max_marginal_relevance_search(
        query,
        k=MMR_K,
        fetch_k=FETCH_K,
        lambda_mult=MMR_LAMBDA,
    )
    if not results:
        print("해당 질문에 대한 답변을 찾을 수 없습니다.")
        return "해당 질문에 대한 답변을 찾을 수 없습니다."

    for i, doc in enumerate(results):
        print(f"============== MMR k={i + 1} ==============")
        print(doc.page_content)

    combined = "\n\n---\n\n".join(d.page_content for d in results)
    print("============== 컨텍스트(합본) ==============")
    print(combined)
    return combined
