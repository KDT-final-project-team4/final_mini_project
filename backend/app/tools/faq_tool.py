from app.config import FETCH_K, MMR_K, MMR_LAMBDA
from app.runtime import get_faq_db


def faq_tool(query: str) -> str:
    db = get_faq_db()
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
