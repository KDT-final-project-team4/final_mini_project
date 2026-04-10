from __future__ import annotations

from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_community.callbacks.manager import get_openai_callback

from app.config import get_response_model


_llm = ChatOpenAI(model=get_response_model(), temperature=0.2)


def response_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    최종 사용자 응답 생성 노드.

    우선순위
    -------
    1. FAQ 흐름이면 evidence_result 기반 응답
    2. callback/action 흐름이면 action_result 기반 응답
    3. vision 흐름이면 vision 응답
    4. 그 외 unsupported / fallback 응답

    핵심 원칙
    --------
    - retrieval 결과는 evidence_result를 우선 사용
    - action 결과는 action_result를 우선 사용
    - tool_result는 하위호환/legacy fallback 용도로만 사용
    """

    intent = (state.get("intent") or "").strip()
    next_action = (state.get("next_action") or "").strip()
    user_input = (state.get("user_input") or "").strip()

    evidence_result = state.get("evidence_result") or {}
    action_result = state.get("action_result") or {}
    tool_result = state.get("tool_result")

    # --------------------------------------------------------------
    # 1. FAQ / 검색 기반 응답
    # --------------------------------------------------------------
    if intent == "faq" or evidence_result:
        final_response = _build_faq_response(
            user_input=user_input,
            evidence_result=evidence_result,
        )

        print("\n[RESPONSE NODE]")
        print("intent:", intent)
        print("has_evidence:", bool(evidence_result))
        print("has_action:", bool(action_result))
        print("final_response:", final_response[:200])

        return {
            **state,
            "final_response": final_response,
        }

    # --------------------------------------------------------------
    # 2. callback 멀티턴 흐름
    # --------------------------------------------------------------
    if next_action == "ask_name":
        final_response = "콜백 접수를 도와드릴게요. 먼저 성함을 알려주세요."

        print("\n[RESPONSE NODE]")
        print("intent:", intent)
        print("has_evidence:", bool(evidence_result))
        print("has_action:", bool(action_result))
        print("final_response:", final_response[:200])

        return {
            **state,
            "final_response": final_response,
        }

    if next_action == "ask_phone":
        collected_name = (state.get("collected_name") or state.get("slots", {}).get("name") or "고객님").strip()
        final_response = f"{collected_name}님, 연락받으실 전화번호를 알려주세요."

        print("\n[RESPONSE NODE]")
        print("intent:", intent)
        print("has_evidence:", bool(evidence_result))
        print("has_action:", bool(action_result))
        print("final_response:", final_response[:200])

        return {
            **state,
            "final_response": final_response,
        }

    if intent == "callback" or action_result:
        callback_response = _build_callback_response(
            action_result=action_result,
            tool_result=tool_result,
            state=state,
        )

        print("\n[RESPONSE NODE]")
        print("intent:", intent)
        print("has_evidence:", bool(evidence_result))
        print("has_action:", bool(action_result))
        print("final_response:", callback_response[:200])

        return {
            **state,
            "final_response": callback_response,
        }

    # --------------------------------------------------------------
    # 3. vision fallback 응답
    # --------------------------------------------------------------
    if intent == "vision_needed" or next_action == "route_vision":
        vision_response = _build_vision_response(
            tool_result=tool_result,
            state=state,
        )

        print("\n[RESPONSE NODE]")
        print("intent:", intent)
        print("has_evidence:", bool(evidence_result))
        print("has_action:", bool(action_result))
        print("final_response:", vision_response[:200])

        return {
            **state,
            "final_response": vision_response,
        }

    # --------------------------------------------------------------
    # 4. unsupported / 기본 fallback
    # --------------------------------------------------------------
    unsupported_response = _build_unsupported_response(
        tool_result=tool_result,
    )

    print("\n[RESPONSE NODE]")
    print("intent:", intent)
    print("has_evidence:", bool(evidence_result))
    print("has_action:", bool(action_result))
    print("final_response:", unsupported_response[:200])

    return {
        **state,
        "final_response": unsupported_response,
    }


def _build_faq_response(
    user_input: str,
    evidence_result: dict[str, Any],
) -> str:
    """
    FAQ 흐름 전용 응답 생성.
    """
    if not evidence_result:
        return "관련 문서를 충분히 찾지 못해 정확한 안내가 어렵습니다. 질문을 조금 더 구체적으로 말씀해 주세요."

    has_evidence = evidence_result.get("has_evidence", False)
    enough_evidence = evidence_result.get("enough_evidence", False)
    needs_clarification = evidence_result.get("needs_clarification", False)
    should_fallback = evidence_result.get("should_fallback", False)
    reason = evidence_result.get("reason", "")
    selected_evidence = evidence_result.get("selected_evidence", [])

    if not has_evidence or reason == "no_results":
        return (
            "현재 등록된 문서에서는 해당 내용을 찾지 못했습니다. "
            "질문을 조금 더 구체적으로 말씀해 주시거나, 필요하시면 담당자 콜백으로 접수해드릴 수 있습니다."
        )

    if should_fallback:
        return (
            "관련된 문서는 일부 찾았지만 현재 질문에 대해 확실하게 안내드릴 만큼 근거가 충분하지 않습니다. "
            "질문을 조금 더 구체적으로 말씀해 주세요."
        )

    if needs_clarification:
        return (
            "질문에 여러 처리 단계가 함께 포함되어 있어 정확히 안내드리려면 범위를 조금 좁히는 것이 좋습니다. "
            "예를 들어 취소 절차, 환불 절차, 교환 절차 중 어떤 내용을 먼저 확인할지 말씀해 주세요."
        )

    context_blocks: list[str] = []

    for idx, item in enumerate(selected_evidence[:1], start=1):
        meta_parts = []

        if item.get("file_name"):
            meta_parts.append(f"문서명: {item['file_name']}")
        if item.get("page") is not None:
            meta_parts.append(f"페이지: {item['page']}")
        if item.get("chunk_index") is not None:
            meta_parts.append(f"청크: {item['chunk_index']}")
        if item.get("score") is not None:
            meta_parts.append(f"유사도: {item['score']:.3f}")

        meta_line = " | ".join(meta_parts)
        content = (item.get("content") or "").strip()[:600]

        block = f"[근거 {idx}]"
        if meta_line:
            block += f"\n{meta_line}"
        block += f"\n{content}"

        context_blocks.append(block)

    context_text = "\n\n".join(context_blocks)

    system_prompt = """
        너는 PDF 매뉴얼 기반 고객상담 AI다.
        제공된 근거 안에서만 답하고, 없는 내용은 지어내지 마라.
        절차형 질문이면 순서대로 짧고 명확하게 설명하라.
    """

    human_prompt = f"""
사용자 질문:
{user_input}

검색 근거:
{context_text}

위 근거만 바탕으로 사용자에게 답변해 주세요.
질문이 절차형이면 처리 순서를 중심으로 짧고 명확하게 설명해 주세요.
"""

    try:
        with get_openai_callback() as cb:
            response = _llm.invoke(
                [
                    SystemMessage(content=system_prompt.strip()),
                    HumanMessage(content=human_prompt.strip()),
                ]
            )

        print("\n[RESPONSE NODE TOKEN USAGE]")
        print("prompt_tokens:", cb.prompt_tokens)
        print("completion_tokens:", cb.completion_tokens)
        print("total_tokens:", cb.total_tokens)
        print("total_cost:", cb.total_cost)

        content = (response.content or "").strip()
        if content:
            return content

    except Exception as error:
        print(f"[RESPONSE NODE] faq llm generation failed: {error}")

    return _build_rule_based_faq_answer(selected_evidence)


def _build_rule_based_faq_answer(selected_evidence: list[dict[str, Any]]) -> str:
    """
    LLM 실패 시 사용할 규칙 기반 FAQ fallback.
    """
    if not selected_evidence:
        return "관련 문서를 찾았지만 현재 답변 생성 중 문제가 발생했습니다."

    first_content = (selected_evidence[0].get("content") or "").strip()
    if not first_content:
        return "관련 문서를 찾았지만 현재 답변 생성 중 문제가 발생했습니다."

    shortened = first_content[:500]
    if len(first_content) > 500:
        shortened += "..."

    return f"문서 기준으로 확인된 내용은 다음과 같습니다.\n\n{shortened}"


def _build_callback_response(
    action_result: dict[str, Any],
    tool_result: Any,
    state: dict[str, Any],
) -> str:
    """
    callback/action 흐름 응답 생성.

    우선순위
    -------
    1. action_result.message
    2. legacy tool_result 문자열/메시지
    3. state 기반 fallback
    """
    if isinstance(action_result, dict):
        message = (action_result.get("message") or "").strip()
        success = action_result.get("success")

        if message:
            return message

        if success is False:
            return "콜백 요청 처리 중 필요한 정보가 부족합니다. 성함과 연락처를 다시 확인해 주세요."

    if isinstance(tool_result, str) and tool_result.strip():
        return tool_result.strip()

    if isinstance(tool_result, dict):
        message = tool_result.get("message")
        if message:
            return str(message)

    collected_name = (state.get("collected_name") or state.get("slots", {}).get("name") or "").strip()
    collected_phone = (state.get("collected_phone") or state.get("slots", {}).get("phone") or "").strip()

    if collected_name and collected_phone:
        return (
            f"{collected_name}님, 요청하신 콜백 접수가 완료되었습니다. "
            f"{collected_phone} 번호로 확인 후 연락드릴 수 있도록 전달하겠습니다."
        )

    return "콜백 요청이 접수되었습니다. 확인 후 연락드릴 수 있도록 전달하겠습니다."


def _build_vision_response(
    tool_result: Any,
    state: dict[str, Any],
) -> str:
    """
    vision fallback 응답 생성.
    """
    if isinstance(tool_result, str) and tool_result.strip():
        return tool_result.strip()

    if isinstance(tool_result, dict):
        message = tool_result.get("message")
        if message:
            return str(message)

    return "정확한 안내를 위해 사진이나 이미지를 먼저 확인해야 합니다. 관련 이미지를 보내주시면 이어서 도와드리겠습니다."


def _build_unsupported_response(tool_result: Any) -> str:
    """
    unsupported 또는 일반 fallback 응답 생성.
    """
    if isinstance(tool_result, str) and tool_result.strip():
        return tool_result.strip()

    if isinstance(tool_result, dict):
        fallback_message = tool_result.get("fallback_message")
        if fallback_message:
            return str(fallback_message)

    return "죄송합니다. 현재 문의에 대해 바로 안내드리기 어렵습니다. 질문을 조금 더 구체적으로 말씀해 주시겠어요?"