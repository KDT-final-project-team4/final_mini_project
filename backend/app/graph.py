from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.state import GraphState

from app.nodes.intent_router import intent_router
from app.nodes.dialogue_manager import dialogue_manager
from app.nodes.faq_node import faq_node
from app.nodes.evidence_check_node import evidence_check_node
from app.nodes.callback_node import callback_node
from app.nodes.vision_node import vision_node
from app.nodes.response_node import response_node


def _route_after_dialogue_manager(state: GraphState) -> str:
    """
    Dialogue Manager가 결정한 next_action 값을 보고
    다음 노드 라우팅 키를 반환한다.

    현재 지원 흐름
    --------------
    - route_faq       -> faq_node
    - ask_name        -> response_node
    - ask_phone       -> response_node
    - route_callback  -> callback_node
    - route_vision    -> vision_node
    - route_unsupported -> response_node

    설계 의도
    --------
    ask_name / ask_phone는 별도 실행 노드가 필요 없는
    '질문 유도 단계'이므로 바로 response_node로 보낸다.
    """
    next_action = (state.get("next_action") or "").strip()

    if next_action == "route_faq":
        return "faq"

    if next_action == "route_callback":
        return "callback"

    if next_action in {"ask_name", "ask_phone", "route_unsupported"}:
        return "response"

    if next_action == "route_vision":
        return "vision"

    # 안전 fallback
    return "response"


def build_graph():
    """
    CallFlow 미니 버전 LangGraph 구성.

    현재 그래프 구조
    ----------------
    START
      -> intent_router
      -> dialogue_manager
         -> faq_node
            -> evidence_check_node
            -> response_node
         -> callback_node
            -> response_node
         -> vision_node
            -> response_node
         -> response_node
      -> END

    핵심 원칙
    --------
    1. Intent Router: 사용자 입력 의도 분류
    2. Dialogue Manager: 다음 행동 결정
    3. FAQ 흐름: retrieval -> evidence check -> response
    4. Callback / Vision 흐름: action -> response
    5. Unsupported / ask 단계: 바로 response
    """

    graph = StateGraph(GraphState)

    # --------------------------------------------------------------
    # Node 등록
    # --------------------------------------------------------------
    graph.add_node("intent_router", intent_router)
    graph.add_node("dialogue_manager", dialogue_manager)

    # FAQ / Retrieval 계열
    graph.add_node("faq_node", faq_node)
    graph.add_node("evidence_check_node", evidence_check_node)

    # Action 계열
    graph.add_node("callback_node", callback_node)
    graph.add_node("vision_node", vision_node)

    # 최종 응답 생성
    graph.add_node("response_node", response_node)

    # --------------------------------------------------------------
    # 시작 흐름
    # --------------------------------------------------------------
    graph.add_edge(START, "intent_router")
    graph.add_edge("intent_router", "dialogue_manager")

    # --------------------------------------------------------------
    # dialogue_manager 이후 분기
    # --------------------------------------------------------------
    graph.add_conditional_edges(
        "dialogue_manager",
        _route_after_dialogue_manager,
        {
            "faq": "faq_node",
            "callback": "callback_node",
            "vision": "vision_node",
            "response": "response_node",
        },
    )

    # --------------------------------------------------------------
    # FAQ 흐름
    # --------------------------------------------------------------
    graph.add_edge("faq_node", "evidence_check_node")
    graph.add_edge("evidence_check_node", "response_node")

    # --------------------------------------------------------------
    # Action 흐름
    # --------------------------------------------------------------
    graph.add_edge("callback_node", "response_node")
    graph.add_edge("vision_node", "response_node")

    # --------------------------------------------------------------
    # 종료
    # --------------------------------------------------------------
    graph.add_edge("response_node", END)

    return graph.compile()


app_graph = build_graph()