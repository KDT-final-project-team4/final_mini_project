from __future__ import annotations

import sys
from pathlib import Path
from copy import deepcopy

# 현재 파일: backend/tests/manual_graph_test.py
# 프로젝트 루트: backend/
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.graph import graph
from app.state import AppState, make_initial_state


WATCH_KEYS = [
    "session_id",
    "user_input",
    "intent",
    "next_action",
    "active_flow",
    "awaiting_field",
    "collected_name",
    "collected_phone",
    "tool_result",
    "final_response",
]


def snapshot_state(state: AppState) -> dict:
    return {key: deepcopy(state.get(key)) for key in WATCH_KEYS}


def print_state(title: str, state: AppState) -> None:
    print(f"\n===== {title} =====")
    for key in WATCH_KEYS:
        print(f"{key}: {state.get(key)}")


def print_state_diff(before: AppState, after: AppState) -> None:
    print("\n[STATE DIFF]")
    changed = False
    for key in WATCH_KEYS:
        before_value = before.get(key)
        after_value = after.get(key)
        if before_value != after_value:
            changed = True
            print(f"- {key}")
            print(f"    before: {before_value}")
            print(f"    after : {after_value}")
    if not changed:
        print("변경된 state 없음")


def run_turn(state: AppState, user_input: str, title: str) -> AppState:
    state["user_input"] = user_input
    before = snapshot_state(state)

    print(f"\n>>> USER INPUT: {user_input}")
    result = graph.invoke(state)

    print_state(title, result)
    print_state_diff(before, result)
    return result


def assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"[FAIL] {label}: expected={expected}, actual={actual}")
    print(f"[PASS] {label}")


def assert_true(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(f"[FAIL] {label}")
    print(f"[PASS] {label}")


def test_faq_flow() -> None:
    print("\n\n########## FAQ FLOW TEST ##########")
    state = make_initial_state("faq-session", "운영시간 알려줘")
    result = graph.invoke(state)

    print_state("FAQ RESULT", result)

    assert_equal(result.get("intent"), "faq", "FAQ intent 분류")
    assert_equal(result.get("next_action"), "run_faq", "FAQ next_action")
    assert_true(result.get("tool_result") is not None, "FAQ tool_result 존재")
    assert_true(result.get("final_response") is not None, "FAQ final_response 존재")


def test_callback_multiturn_flow() -> None:
    print("\n\n########## CALLBACK MULTI-TURN TEST ##########")
    state = make_initial_state("callback-session")

    state = run_turn(state, "상담원 연결해줘", "CALLBACK START")
    assert_equal(state.get("intent"), "callback", "Callback intent 분류")
    assert_equal(state.get("active_flow"), "callback", "Callback flow 시작")
    assert_equal(state.get("awaiting_field"), "name", "이름 입력 대기")
    assert_equal(state.get("next_action"), "ask_name", "ask_name 분기")
    assert_true(state.get("final_response") is not None, "이름 요청 응답 존재")

    state = run_turn(state, "홍길동", "CALLBACK NAME")
    assert_equal(state.get("active_flow"), "callback", "이름 입력 후 callback 유지")
    assert_equal(state.get("awaiting_field"), "phone", "전화번호 입력 대기")
    assert_equal(state.get("collected_name"), "홍길동", "이름 저장")
    assert_equal(state.get("next_action"), "ask_phone", "ask_phone 분기")
    assert_true(state.get("final_response") is not None, "전화번호 요청 응답 존재")

    state = run_turn(state, "010-1234-5678", "CALLBACK PHONE")
    assert_equal(state.get("next_action"), "finish", "callback 완료")
    assert_equal(state.get("active_flow"), None, "callback 종료 후 active_flow 초기화")
    assert_equal(state.get("awaiting_field"), None, "callback 종료 후 awaiting_field 초기화")
    assert_equal(state.get("collected_name"), None, "callback 종료 후 collected_name 초기화")
    assert_equal(state.get("collected_phone"), None, "callback 종료 후 collected_phone 초기화")
    assert_true(state.get("tool_result") is not None, "callback tool_result 존재")
    assert_true(state.get("final_response") is not None, "callback 완료 응답 존재")


def test_vision_fallback_flow() -> None:
    print("\n\n########## VISION FALLBACK TEST ##########")
    state = make_initial_state("vision-session", "이거 이상해요")
    result = graph.invoke(state)

    print_state("VISION RESULT", result)

    assert_equal(result.get("next_action"), "run_vision", "Vision fallback next_action")
    assert_true(result.get("tool_result") is not None, "Vision tool_result 존재")
    assert_true(result.get("final_response") is not None, "Vision final_response 존재")


def test_invalid_input_handling() -> None:
    print("\n\n########## INVALID INPUT TEST ##########")
    state = make_initial_state("invalid-session")

    state = run_turn(state, "상담원 연결해줘", "INVALID START")
    assert_equal(state.get("awaiting_field"), "name", "이름 대기 상태 진입")

    state = run_turn(state, "운영시간 알려줘", "INVALID NAME INPUT")
    assert_equal(state.get("active_flow"), "callback", "잘못된 이름 입력 후 callback 유지")
    assert_equal(state.get("awaiting_field"), "name", "이름 재입력 대기 유지")
    assert_equal(state.get("next_action"), "ask_name", "이름 재요청")
    assert_true(state.get("tool_result") is not None, "이름 검증 실패 tool_result 존재")
    assert_true(state.get("final_response") is not None, "이름 재입력 응답 존재")

    state = run_turn(state, "홍길동", "VALID NAME AFTER INVALID")
    assert_equal(state.get("awaiting_field"), "phone", "정상 이름 입력 후 전화번호 대기")

    state = run_turn(state, "010123", "INVALID PHONE INPUT")
    assert_equal(state.get("active_flow"), "callback", "잘못된 전화번호 입력 후 callback 유지")
    assert_equal(state.get("awaiting_field"), "phone", "전화번호 재입력 대기 유지")
    assert_equal(state.get("next_action"), "ask_phone", "전화번호 재요청")
    assert_true(state.get("tool_result") is not None, "전화번호 검증 실패 tool_result 존재")
    assert_true(state.get("final_response") is not None, "전화번호 재입력 응답 존재")


def test_empty_input_handling() -> None:
    print("\n\n########## EMPTY INPUT TEST ##########")
    state = make_initial_state("empty-session", "")
    result = graph.invoke(state)

    print_state("EMPTY INPUT RESULT", result)

    assert_equal(result.get("next_action"), "run_vision", "빈 입력 fallback 분기")
    assert_true(result.get("final_response") is not None, "빈 입력 final_response 존재")


def run_all_tests() -> None:
    test_faq_flow()
    test_callback_multiturn_flow()
    test_vision_fallback_flow()
    test_invalid_input_handling()
    test_empty_input_handling()
    print("\n\n모든 수동 테스트가 완료되었습니다.")


if __name__ == "__main__":
    run_all_tests()