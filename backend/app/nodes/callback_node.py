from __future__ import annotations

from typing import Any

from app.tools.callback_tool import register_callback_tool


def callback_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    callback 실행 노드.

    역할
    ----
    1. state에서 name, phone을 읽는다.
    2. register_callback_tool()을 호출한다.
    3. 결과를 action_result에 저장한다.
    4. response_node가 사용할 수 있도록 최소 message도 같이 유지한다.

    설계 원칙
    ----------
    - 이 노드는 '실행'만 담당한다.
    - 흐름 제어는 dialogue_manager가 한다.
    - 결과는 구조화된 형태(action_result)로 저장한다.
    """

    name = (state.get("collected_name") or "").strip()
    phone = (state.get("collected_phone") or "").strip()

    # --------------------------------------------------------------
    # 1. callback tool 실행
    # --------------------------------------------------------------
    action_result = register_callback_tool(name=name, phone=phone)

    print("\n[CALLBACK NODE]")
    print("name:", name)
    print("phone:", phone)
    print("action_result:", action_result)

    # --------------------------------------------------------------
    # 2. message 추출 (하위호환)
    # --------------------------------------------------------------
    message = ""
    if isinstance(action_result, dict):
        message = (action_result.get("message") or "").strip()

    # --------------------------------------------------------------
    # 3. debug_info 기록
    # --------------------------------------------------------------
    debug_info = dict(state.get("debug_info") or {})
    debug_info["callback_node"] = {
        "action": "register_callback",
        "name": name,
        "phone": phone,
        "success": action_result.get("success") if isinstance(action_result, dict) else None,
    }

    # --------------------------------------------------------------
    # 4. state 반환
    # --------------------------------------------------------------
    return {
        **state,
        "action_result": action_result,
        # 기존 response_node 호환을 위해 tool_result도 같이 유지 (점진적 제거 예정)
        "tool_result": message,
        "active_flow": "",  # callback 흐름 종료
        "debug_info": debug_info,
    }