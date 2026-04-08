from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from app.prompts.dialogue_prompt import get_dialogue_prompt
import os


load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# dialogue_manager node
def run(state):

    user_input = state.get('user_input')

    llm = ChatGoogleGenerativeAI(
        model='models/gemini-2.5-pro',
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2
    )

    prompt = get_dialogue_prompt()
    prompt_template = ChatPromptTemplate.from_template(prompt)

    chain = prompt_template | llm

    response = chain.invoke({
        'user_input': user_input
    })

    state['final_response'] = response
    return state
