# faq prompt
def get_faq_prompt(user_question: str, search_result: str):
    prompt = f"""
    FAQ 질문: {user_question}
    FAQ 검색 결과: {search_result}


    FAQ 검색 결과를 바탕으로 FAQ 질문에 대한 답변을 생성해 주세요.
    모르겠다면 모른다고 솔직하게 답변해 주세요.
    """
    return prompt


def get_keyword_prompt(user_question: str) -> str:
    prompt = (
        "너는 검색 쿼리 최적화 전문가야. 사용자의 질문에서 불용어(조사, 어미, 인사말 등)를 제거하고, "
        "지식 베이스 검색에 가장 적합한 핵심 명사 키워드만 뽑아줘. "
        "결과는 반드시 단어 형태로만 출력해.\n\n"
        f"질문: {user_question}\n"
        "키워드:"
    )
    return prompt
