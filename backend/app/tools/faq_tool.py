def faq_tool(query: str) -> str:
    """
    간단한 FAQ 응답 (RAG 대신 mock)
    """
    normalized_query = query.lower().replace(" ", "")

    if any(keyword in normalized_query for keyword in ["운영시간", "영업시간", "진료시간"]):
        return "운영시간은 09:00~18:00 입니다."

    if "주차" in normalized_query:
        return "건물 뒤편 주차장을 이용하실 수 있습니다."

    return "해당 질문에 대한 답변을 찾지 못했습니다."