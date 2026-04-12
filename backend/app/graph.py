from __future__ import annotations

from langgraph.graph import END, StateGraph

try:
    from app.state import CallFlowState
    from app.nodes.intent_router import intent_router
    from app.nodes.dialogue_manager import dialogue_manager
    from app.nodes.faq_node import faq_node
    from app.nodes.callback_node import callback_node
    from app.nodes.vision_node import vision_node
    from app.nodes.response_node import response_node
except ImportError:  # local test fallback
    from state import CallFlowState
    from intent_router import intent_router
    from dialogue_manager import dialogue_manager
    from faq_node import faq_node
    from callback_node import callback_node
    from vision_node import vision_node
    from response_node import response_node


def _route_after_dialogue(state: CallFlowState) -> str:
    next_action = state.get("next_action")

    if next_action == "run_faq":
        return "faq"

    if next_action in {"ask_name", "ask_phone", "run_callback"}:
        return "callback"

    if next_action == "run_vision":
        return "vision"

    return "response"


def build_graph():
    graph = StateGraph(CallFlowState)

    graph.add_node("intent_router", intent_router)
    graph.add_node("dialogue_manager", dialogue_manager)
    graph.add_node("faq_node", faq_node)
    graph.add_node("callback_node", callback_node)
    graph.add_node("vision_node", vision_node)
    graph.add_node("response_node", response_node)

    graph.set_entry_point("intent_router")

    # 1) intent 분류
    graph.add_edge("intent_router", "dialogue_manager")

    # 2) dialogue_manager가 next_action 결정
    graph.add_conditional_edges(
        "dialogue_manager",
        _route_after_dialogue,
        {
            "faq": "faq_node",
            "callback": "callback_node",
            "vision": "vision_node",
            "response": "response_node",
        },
    )

    # 3) 각 실행 노드 후 최종 응답 생성
    graph.add_edge("faq_node", "response_node")
    graph.add_edge("callback_node", "response_node")
    graph.add_edge("vision_node", "response_node")

    # 4) 종료
    graph.add_edge("response_node", END)

    return graph.compile()


app_graph = build_graph()


if __name__ == "__main__":
    sample_state: CallFlowState = {
        "session_id": "graph-test-1",
        "user_input": "상담원 연결해줘",
        "intent": None,
        "next_action": None,
        "active_flow": None,
        "awaiting_field": None,
        "collected_name": None,
        "collected_phone": None,
        "tool_result": None,
        "final_response": None,
    }

    result = app_graph.invoke(sample_state)
    print(result)