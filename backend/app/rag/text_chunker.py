from __future__ import annotations

from typing import Any

from app.rag.faq_loader import build_faq_source_text


def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 80) -> list[str]:
    clean = (text or "").strip()
    if not clean:
        return []

    if len(clean) <= chunk_size:
        return [clean]

    chunks: list[str] = []
    start = 0
    text_len = len(clean)

    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk = clean[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= text_len:
            break

        start = max(0, end - chunk_overlap)

    return chunks


def create_faq_chunks(
    docs: list[dict[str, Any]],
    *,
    chunk_size: int = 500,
    chunk_overlap: int = 80,
) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []

    for doc in docs:
        source_text = build_faq_source_text(doc)
        split_chunks = chunk_text(
            source_text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        for chunk_index, chunk_text_value in enumerate(split_chunks):
            chunks.append(
                {
                    "id": f"{doc['id']}::chunk-{chunk_index}",
                    "source_id": doc["id"],
                    "chunk_index": chunk_index,
                    "text": chunk_text_value,
                    "question": doc.get("question", ""),
                    "answer": doc.get("answer", ""),
                    "category": doc.get("category", ""),
                    "keywords": doc.get("keywords", []),
                }
            )

    return chunks