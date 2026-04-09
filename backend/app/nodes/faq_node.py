# faq_node node
from app.state import CallFlowState
from app.tools.faq_tool import faq_tool

def run(state: CallFlowState) -> CallFlowState:
    """
    FAQ Specialist Agent Node
    - 사용자 질문을 받아 FAQ Tool(RAG 검색)을 실행
    - 검색 결과를 tool_result에 저장
    - 최종 응답 생성은 response_node에서 처리
    """
    user_input = state.get('user_input', '').strip()

    result = faq_tool(user_input)

    state['tool_result'] = result

    print('[FAQ Node]')
    print(' user_input:', user_input)
    print(' tool_result:', result)
    
    return state
