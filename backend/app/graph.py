# LangGraph 구조 작성
from langgraph.graph import END, START, StateGraph

from app.state import CallFlowState
from app.nodes.intent_router import run as intent_router_node
from app.nodes.dialogue_manager import run as dialogue_manager_node
from app.nodes.faq_node import run as faq_node
from app.nodes.callback_node import run as callback_node
from app.nodes.vision_node import run as vision_node
from app.nodes.response_node import run as response_node

def route_by_action(state: CallFlowState) -> str:
    """
    Dialogue Manager가 정한 next_action 값을 보고
    다음 노드로 분기한다.
    """
    action = state.get('next_action')

    if action == 'call_faq':
        return 'faq_node'
    
    if action == 'call_callback':
        return 'callback_node'
    
    if action == 'trigger_vision':
        return 'vision_node'
    
    return 'response_node'

def build_graph():
    graph = StateGraph(CallFlowState)

    # 노드 등록
    graph.add_node('intent_router', intent_router_node)
    graph.add_node('dialogue_manager', dialogue_manager_node)
    graph.add_node('faq_node', faq_node)
    graph.add_node('callback_node', callback_node)
    graph.add_node('vision_node', vision_node)
    graph.add_node('response_node', response_node)

    # 시작 흐름
    graph.add_edge(START, 'intent_router')
    graph.add_edge('intent_router', 'dialogue_manager')

    # 조건 분기
    graph.add_conditional_edges(
        'dialogue_manager', 
        route_by_action,
        {
            'faq_node': 'faq_node',
            'callback_node': 'callback_node',
            'vision_node': 'vision_node',
            'response_node': 'response_node',
        },
    )

    # tool node 실행 후 response로 이동
    graph.add_edge('faq_node', 'response_node')
    graph.add_edge('callback_node', 'response_node')
    graph.add_edge('vision_node', 'response_node')

    # 응답 후 종료
    graph.add_edge('response_node', END)

    return graph.compile()
    
    
    