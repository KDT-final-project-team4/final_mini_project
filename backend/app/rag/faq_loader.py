from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _normalize_keywords(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, str):
        return [x.strip() for x in value.split(",") if x.strip()]
    return []


def load_faq_documents(path: str | Path) -> list[dict[str, Any]]:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"FAQ document file not found: {file_path}")

    raw = json.loads(file_path.read_text(encoding="utf-8"))

    if isinstance(raw, dict) and "documents" in raw:
        raw_docs = raw["documents"]
    elif isinstance(raw, list):
        raw_docs = raw
    else:
        raise ValueError("FAQ document file must be a list or {'documents': [...]} format.")

    documents: list[dict[str, Any]] = []

    for idx, item in enumerate(raw_docs, start=1):
        if not isinstance(item, dict):
            continue

        question = str(item.get("question", "")).strip()
        answer = str(item.get("answer", "")).strip()
        category = str(item.get("category", "")).strip()
        doc_id = str(item.get("id", f"faq-{idx:04d}")).strip()
        keywords = _normalize_keywords(item.get("keywords"))

        if not question or not answer:
            continue

        documents.append(
            {
                "id": doc_id,
                "category": category,
                "question": question,
                "answer": answer,
                "keywords": keywords,
            }
        )

    return documents


def build_faq_source_text(doc: dict[str, Any]) -> str:
    category = doc.get("category", "")
    question = doc.get("question", "")
    answer = doc.get("answer", "")
    keywords = ", ".join(doc.get("keywords", []))

    parts = [
        f"카테고리: {category}" if category else "",
        f"키워드: {keywords}" if keywords else "",
        f"질문: {question}",
        f"답변: {answer}",
    ]
    return "\n".join([part for part in parts if part]).strip()