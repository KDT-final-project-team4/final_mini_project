from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from app.prompts.response_prompt import get_response_prompt

# response_node node


def run(state):

    user_input = state.get("user_input")
    intent = state.get("intent")
    tool_result = state.get("tool_result")

    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.5-pro",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    prompt = get_response_prompt()
    prompt_template = ChatPromptTemplate.from_template(prompt)

    chain = prompt_template | llm

    response = chain.invoke(
        {
            "user_input": user_input,
            "intent": intent,
            "tool_result": tool_result if tool_result is not None else "",
        }
    )

    return {"final_response": response.content.strip()}
