# LangGraph 구조 작성 예정
from langgraph.graph import StateGraph, START, END
from app.nodes.intent_router import run as intent_router_run
from app.nodes.faq_node import run as faq_node_run
from app.nodes.callback_node import run as callback_node_run
from app.nodes.response_node import run as response_node_run
from app.nodes.vision_node import run as vision_node_run
from app.nodes.dialogue_manager import run as dialogue_manager_run

# intent 노드의 반환 결과를 보고 다음 노드로 라우팅하는 함수
def route_by_intent(state):
    intent = state.get('intent')
    
    if intent == 'faq':
        return "FAQ_NODE"
    elif intent == 'callback':
        return "CALLBACK_NODE"
    elif intent == 'vision':
        return "VISION_NODE"
    elif intent == 'dialogue':
        return "DIALOGUE_NODE"
    else:
        return "RESPONSE_NODE"


def build_graph():

    graph = StateGraph()

    graph.add_node('intent_router', intent_router_run)
    graph.add_node(START, intent_router_run)

    # node 등록
    graph.add_node('FAQ_NODE', faq_node_run)
    graph.add_node('CALLBACK_NODE', callback_node_run)
    graph.add_node('VISION_NODE', vision_node_run)
    graph.add_node('DIALOGUE_NODE', dialogue_manager_run)
    graph.add_node('RESPONSE_NODE', response_node_run)


    # 의도(intent)에 따라 FAQ, 콜백, 비전, 일반 응답 노드로 분기
    graph.add_conditional_edges(
        'intent_router',
        route_by_intent,
        {
            'faq': 'FAQ_NODE',
            'callback': 'CALLBACK_NODE',
            'vision': 'VISION_NODE',
            'dialogue': 'DIALOGUE_NODE',
        }
    )

    graph.add_edge('FAQ_NODE', 'RESPONSE_NODE')
    graph.add_edge('CALLBACK_NODE', 'RESPONSE_NODE')
    graph.add_edge('VISION_NODE', 'RESPONSE_NODE')
    graph.add_edge('DIALOGUE_NODE', 'RESPONSE_NODE')
    graph.add_edge('RESPONSE_NODE', END)

    return graph