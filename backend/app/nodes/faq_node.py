from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.config import FAQ_LLM_MODEL
from app.prompts.faq_prompt import get_faq_prompt, get_keyword_prompt
from app.tools.faq_tool import faq_tool


# faq_node node
def run(state):
    user_question = state.get("user_input")

    llm = ChatOpenAI(
        model=FAQ_LLM_MODEL,
        temperature=0,
        max_retries=2,
    )

    # 키워드 추출
    keywords = get_keyword_prompt(user_question)
    keywords_prompt_template = ChatPromptTemplate.from_template(keywords)
    keywords_chain = keywords_prompt_template | llm

    keywords_response = keywords_chain.invoke({"user_question": user_question})
    print(f"키워드 추출 결과: {keywords_response.content.strip()}")

    # 검색 결과 추출
    search_result = faq_tool(keywords_response.content.strip())
    print(f"검색 결과 추출 결과: {search_result}")

    # FAQ 답변 생성 (get_faq_prompt가 이미 전체 문맥 문자열을 만듦 → str만 llm에 전달)
    faq_prompt = get_faq_prompt(user_question, search_result)
    response = llm.invoke(faq_prompt)
    print(f"FAQ 답변 생성 결과: {response.content.strip()}")
    return {"final_response": response.content.strip()}
