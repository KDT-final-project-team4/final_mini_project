from langchain_core.prompts import ChatPromptTemplate

from app.prompts.response_prompt import get_response_prompt
from app.runtime import get_chat_llm

# response_node node


def run(state):

    user_input = state.get("user_input")
    intent = state.get("intent")
    tool_result = state.get("tool_result")

    llm = get_chat_llm()

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
