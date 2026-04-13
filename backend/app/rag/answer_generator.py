from __future__ import annotations

from typing import Any


NOT_FOUND_MESSAGE = "지금 확인 가능한 FAQ 문서에서 관련 정보를 찾지 못했어요. 질문을 조금 더 구체적으로 말씀해주세요."


def _build_extract_answer(hits: list[dict[str, Any]]) -> dict[str, Any]:
    if not hits:
        return {
            "answer": NOT_FOUND_MESSAGE,
            "mode": "extractive",
        }

    top_hit = hits[0]
    metadata = top_hit.get("metadata") or {}

    answer = str(metadata.get("answer", "")).strip()
    question = str(metadata.get("question", "")).strip()

    if answer:
        return {
            "answer": answer,
            "mode": "extractive",
            "matched_question": question,
        }

    text = str(top_hit.get("text", "")).strip()
    if text:
        return {
            "answer": text,
            "mode": "extractive",
            "matched_question": question,
        }

    return {
        "answer": NOT_FOUND_MESSAGE,
        "mode": "extractive",
    }


def generate_faq_answer(query: str, hits: list[dict[str, Any]]) -> dict[str, Any]:
    _ = query
    return _build_extract_answer(hits)