from __future__ import annotations

import time
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.graph import app_graph
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="CallFlow Mini Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 중에는 일단 전체 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# Request / Response Schema
# ------------------------------------------------------------------
class ChatRequest(BaseModel):
    """
    프론트에서 /chat 으로 보내는 요청 형식.

    message:
        현재 턴의 사용자 입력

    session_state:
        프론트가 이전 턴까지 유지하고 있던 상태
        (이름, 전화번호, active_flow 등)
    """

    message: str = Field(..., description="현재 사용자 입력")
    session_state: dict[str, Any] | None = Field(
        default=None,
        description="이전 턴까지의 세션 상태",
    )


class ChatResponse(BaseModel):
    """
    /chat 응답 형식.

    answer:
        사용자에게 보여줄 최종 응답

    session_state:
        다음 턴에서 다시 프론트가 보관/전달할 상태

    debug_info:
        개발/실험용 정보
        (추후 Gemma 4 비교 시 latency, node별 로그 등에 활용 가능)
    """

    answer: str
    session_state: dict[str, Any]
    debug_info: dict[str, Any] | None = None


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def _generate_session_id() -> str:
    """
    session_id가 없을 때 사용할 간단한 UUID 생성.
    """
    return str(uuid.uuid4())


def _build_initial_state(
    message: str,
    session_state: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    프론트에서 전달받은 session_state와 현재 message를 합쳐
    LangGraph 실행용 초기 state를 만든다.

    설계 원칙
    ----------
    1. 현재 턴 입력은 항상 user_input에 넣는다.
    2. 이전 턴 상태(session_state)는 최대한 유지한다.
    3. 턴마다 다시 계산될 값(tool_result, evidence_result, final_response 등)은 새 턴 시작 시 비워준다.
    4. session_id, tenant_id, debug_info 같은 확장 필드도 안전하게 유지한다.
    """
    prev_state = dict(session_state or {})

    initial_state = {
        # ----------------------------------------------------------
        # 현재 턴 입력
        # ----------------------------------------------------------
        "user_input": message.strip(),

        # ----------------------------------------------------------
        # 이전 세션 상태 유지
        # ----------------------------------------------------------
        "intent": prev_state.get("intent", ""),
        "next_action": prev_state.get("next_action", ""),
        "active_flow": prev_state.get("active_flow", ""),
        "collected_name": prev_state.get("collected_name", ""),
        "collected_phone": prev_state.get("collected_phone", ""),
        "slots": prev_state.get("slots", {}),

        # ----------------------------------------------------------
        # retrieval / evidence / action 결과
        # 새 턴에서 다시 계산되므로 기본적으로 초기화
        # ----------------------------------------------------------
        "tool_result": {},
        "retrieval_preview": "",
        "evidence_result": {},
        "action_result": {},

        # ----------------------------------------------------------
        # 최종 응답도 새 턴에서 다시 생성
        # ----------------------------------------------------------
        "final_response": "",

        # ----------------------------------------------------------
        # 세션 / 멀티테넌시 확장 대비
        # ----------------------------------------------------------
        "session_id": prev_state.get("session_id") or _generate_session_id(),
        "tenant_id": prev_state.get("tenant_id", "default"),

        # ----------------------------------------------------------
        # guardrail / 디버깅 정보
        # ----------------------------------------------------------
        "guardrail_flags": prev_state.get("guardrail_flags", {}),
        "messages": prev_state.get("messages", []),
        "debug_info": prev_state.get("debug_info", {}),
    }

    return initial_state


def _extract_session_state_for_client(graph_state: dict[str, Any]) -> dict[str, Any]:
    """
    LangGraph 실행 결과에서 다음 턴에 프론트가 계속 들고 있어야 할
    핵심 state만 추려서 반환한다.

    왜 전체 state를 그대로 안 보내는가?
    -------------------------------
    retrieval 결과 전체, evidence 요약 전체를 매 턴 프론트가 모두 들고 있을 필요는 없다.
    프론트는 대화 흐름에 필요한 최소 상태만 보관하면 된다.

    다만 디버깅/실험 편의를 위해 retrieval_preview 정도는 남겨둔다.
    """
    return {
        "session_id": graph_state.get("session_id", ""),
        "tenant_id": graph_state.get("tenant_id", "default"),
        "intent": graph_state.get("intent", ""),
        "next_action": graph_state.get("next_action", ""),
        "active_flow": graph_state.get("active_flow", ""),
        "collected_name": graph_state.get("collected_name", ""),
        "collected_phone": graph_state.get("collected_phone", ""),
        "slots": graph_state.get("slots", {}),
        "retrieval_preview": graph_state.get("retrieval_preview", ""),
        "guardrail_flags": graph_state.get("guardrail_flags", {}),
        "debug_info": graph_state.get("debug_info", {}),
    }


def _append_message_trace(
    state: dict[str, Any],
    role: str,
    content: str,
) -> None:
    """
    간단한 메시지 trace를 state["messages"]에 추가한다.

    현재는 최소 구조만 남긴다.
    나중에 음성/WebSocket/상담 로그 저장으로 확장 가능하다.
    """
    if "messages" not in state or not isinstance(state["messages"], list):
        state["messages"] = []

    state["messages"].append(
        {
            "role": role,
            "content": content,
        }
    )


# ------------------------------------------------------------------
# Route
# ------------------------------------------------------------------
@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """
    텍스트 기반 CallFlow 미니 버전의 핵심 엔드포인트.

    처리 순서
    --------
    1. 프론트에서 받은 message + session_state를 병합
    2. LangGraph 실행
    3. final_response 추출
    4. 다음 턴용 session_state 반환
    5. latency/debug 정보 반환
    """
    user_message = (request.message or "").strip()

    if not user_message:
        raise HTTPException(status_code=400, detail="message는 비어 있을 수 없습니다.")

    started_at = time.perf_counter()

    try:
        # ----------------------------------------------------------
        # 1. 초기 state 생성
        # ----------------------------------------------------------
        initial_state = _build_initial_state(
            message=user_message,
            session_state=request.session_state,
        )

        print("\n=== [REQUEST] ===")
        print("user_input:", user_message)
        print("prev_session_state:", request.session_state)

        _append_message_trace(initial_state, "user", user_message)

        print("\n=== [INITIAL STATE] ===")
        print(initial_state)

        # ----------------------------------------------------------
        # 2. LangGraph 실행
        # ----------------------------------------------------------
        result_state = app_graph.invoke(initial_state)

        print("\n=== [GRAPH RESULT] ===")
        print(result_state)

        if not isinstance(result_state, dict):
            raise RuntimeError("LangGraph 실행 결과가 dict 형태가 아닙니다.")

        # ----------------------------------------------------------
        # 3. final_response 추출
        # ----------------------------------------------------------
        answer = (result_state.get("final_response") or "").strip()

        if not answer:
            answer = "죄송합니다. 현재 답변을 생성하지 못했습니다. 다시 한 번 말씀해 주세요."

        _append_message_trace(result_state, "assistant", answer)

        # ----------------------------------------------------------
        # 4. 디버그 정보 구성
        # ----------------------------------------------------------
        elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2)

        debug_info = dict(result_state.get("debug_info") or {})
        debug_info.update(
            {
                "session_id": result_state.get("session_id", ""),
                "latency_ms": elapsed_ms,
                "intent": result_state.get("intent", ""),
                "next_action": result_state.get("next_action", ""),
                "active_flow": result_state.get("active_flow", ""),
                "has_tool_result": bool(result_state.get("tool_result")),
                "has_evidence_result": bool(result_state.get("evidence_result")),
            }
        )

        result_state["debug_info"] = debug_info

        # ----------------------------------------------------------
        # 5. 프론트로 돌려줄 session_state 정리
        # ----------------------------------------------------------
        next_session_state = _extract_session_state_for_client(result_state)

        return ChatResponse(
            answer=answer,
            session_state=next_session_state,
            debug_info=debug_info,
        )

    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"/chat 처리 중 오류가 발생했습니다: {error}",
        ) from error