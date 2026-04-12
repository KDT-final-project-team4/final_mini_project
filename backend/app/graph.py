from langgraph.graph import StateGraph, START, END
from app.state import State
from app.nodes.intent_router import intent_router_node
from app.nodes.dialogue_manager import dialogue_manager_node
from app.nodes.response_node import response_node

# 1. 상태(State)를 기반으로 하는 그래프 초기화
workflow = StateGraph(State)

# 2. 그래프에 노드 등록하기 (이름, 실행할 함수)
workflow.add_node("intent_router", intent_router_node)
workflow.add_node("dialogue_manager", dialogue_manager_node)
workflow.add_node("response_node", response_node)

# 3. 노드 간의 엣지(흐름) 연결하기
# 시작 -> 의도 파악 -> 대화 관리(분기 결정) -> 응답 생성 -> 끝
workflow.add_edge(START, "intent_router")
workflow.add_edge("intent_router", "dialogue_manager")
workflow.add_edge("dialogue_manager", "response_node")
workflow.add_edge("response_node", END)

# 4. 그래프 컴파일 (실행 가능한 애플리케이션으로 변환)
app = workflow.compile()