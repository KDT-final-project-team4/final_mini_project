from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from app.prompts.response_prompt import get_response_prompt

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# response_node node

def run(state):

    user_input = state.get('user_input')
    intent = state.get('intent')
    tool_result = state.get('tool_result')

    llm = ChatGoogleGenerativeAI(
        model='gemini-2.5-flash',
        temperature=0.3,
        max_tokens=None,
        timeout=None,
        max_retries=2
    )

    prompt = get_response_prompt()
    prompt_template = ChatPromptTemplate.from_template(prompt)

    chain = prompt_template | llm

    response = chain.invoke({
        'user_input': user_input,
        'intent': intent,
        'tool_result': tool_result
    })

    return {
        'final_response': response.content.strip()
    }
