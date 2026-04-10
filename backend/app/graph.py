from __future__ import annotations

from typing import Any, Literal

from langgraph.graph import START, END, StateGraph

try:
    from app.state import AppState, make_initial_state
    from app.nodes.intent_router import intent_router
    from app.nodes.dialogue_manager import dialogue_manager
    from app.nodes.faq_node import faq_node
    from app.nodes.callback_node import callback_node
    from app.nodes.vision_node import vision_node
    from app.nodes.response_node import response_node
except ImportError:  # local test fallback
    from state import AppState, make_initial_state
    from intent_router import intent_router
    from dialogue_manager import dialogue_manager
    from faq_node import faq_node
    from callback_node import callback_node
    from vision_node import vision_node
    from response_node import response_node


NextNode = Literal["faq_node", "callback_node", "vision_node", "response_node"]


def route_after_dialogue_manager(state: AppState) -> NextNode:
    """
    dialogue_manager가 정한 next_action 기준으로 다음 노드를 결정한다.
    """
    next_action = state.get("next_action")

    if next_action == "run_faq":
        return "faq_node"

    if next_action in {"ask_name", "ask_phone", "run_callback"}:
        return "callback_node"

    if next_action == "run_vision":
        return "vision_node"

    return "response_node"


def build_graph(*, checkpointer: Any | None = None):
    """
    LangGraph 빌드 함수.
    """
    builder = StateGraph(AppState)

    builder.add_node("intent_router", intent_router)
    builder.add_node("dialogue_manager", dialogue_manager)
    builder.add_node("faq_node", faq_node)
    builder.add_node("callback_node", callback_node)
    builder.add_node("vision_node", vision_node)
    builder.add_node("response_node", response_node)

    builder.add_edge(START, "intent_router")
    builder.add_edge("intent_router", "dialogue_manager")

    builder.add_conditional_edges(
        "dialogue_manager",
        route_after_dialogue_manager,
        {
            "faq_node": "faq_node",
            "callback_node": "callback_node",
            "vision_node": "vision_node",
            "response_node": "response_node",
        },
    )

    builder.add_edge("faq_node", "response_node")
    builder.add_edge("callback_node", "response_node")
    builder.add_edge("vision_node", "response_node")
    builder.add_edge("response_node", END)

    return builder.compile(checkpointer=checkpointer)


graph = build_graph()


if __name__ == "__main__":
    # smoke test 1: FAQ
    faq_input: AppState = make_initial_state("faq-1", "영업시간이 어떻게 돼?")
    faq_result = graph.invoke(faq_input)
    print("[FAQ RESULT]")
    print(faq_result)
    print("final_response:", faq_result.get("final_response"))

    # smoke test 2: Callback 시작
    callback_start_input: AppState = make_initial_state("callback-1", "상담 콜백 요청할게요")
    callback_start_result = graph.invoke(callback_start_input)
    print("\n[CALLBACK START RESULT]")
    print(callback_start_result)
    print("final_response:", callback_start_result.get("final_response"))

    # smoke test 3: Callback 이름 입력
    callback_name_input: AppState = {
        "session_id": "callback-1",
        "user_input": "홍길동",
        "intent": "callback",
        "next_action": None,
        "active_flow": "callback",
        "awaiting_field": "name",
        "collected_name": None,
        "collected_phone": None,
        "tool_result": None,
        "final_response": None,
    }
    callback_name_result = graph.invoke(callback_name_input)
    print("\n[CALLBACK NAME RESULT]")
    print(callback_name_result)
    print("final_response:", callback_name_result.get("final_response"))

    # smoke test 4: Callback 전화번호 입력
    callback_phone_input: AppState = {
        "session_id": "callback-1",
        "user_input": "010-1234-5678",
        "intent": "callback",
        "next_action": None,
        "active_flow": "callback",
        "awaiting_field": "phone",
        "collected_name": "홍길동",
        "collected_phone": None,
        "tool_result": None,
        "final_response": None,
    }
    callback_phone_result = graph.invoke(callback_phone_input)
    print("\n[CALLBACK PHONE RESULT]")
    print(callback_phone_result)
    print("final_response:", callback_phone_result.get("final_response"))