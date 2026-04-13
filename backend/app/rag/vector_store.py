from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb

from app.rag.embeddings import FAQEmbedder


class FAQVectorStore:
    def __init__(self, persist_dir: str, collection_name: str) -> None:
        self.persist_dir = persist_dir
        self.collection_name = collection_name

        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection = self.client.get_or_create_collection(name=self.collection_name)

    def upsert_chunks(
        self,
        chunks: list[dict[str, Any]],
        *,
        embedder: FAQEmbedder,
    ) -> dict[str, Any]:
        if not chunks:
            return {
                "ok": True,
                "upserted_count": 0,
                "collection_name": self.collection_name,
            }

        ids = [str(chunk["id"]) for chunk in chunks]
        documents = [str(chunk["text"]) for chunk in chunks]
        embeddings = embedder.embed_documents(documents)

        metadatas: list[dict[str, Any]] = []
        for chunk in chunks:
            metadatas.append(
                {
                    "source_id": str(chunk.get("source_id", "")),
                    "chunk_index": int(chunk.get("chunk_index", 0)),
                    "question": str(chunk.get("question", "")),
                    "answer": str(chunk.get("answer", "")),
                    "category": str(chunk.get("category", "")),
                    "keywords": ", ".join(chunk.get("keywords", [])),
                }
            )

        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

        return {
            "ok": True,
            "upserted_count": len(ids),
            "collection_name": self.collection_name,
        }

    def query(
        self,
        query_text: str,
        *,
        embedder: FAQEmbedder,
        top_k: int = 3,
    ) -> list[dict[str, Any]]:
        query_embedding = embedder.embed_query(query_text)
        if not query_embedding:
            return []

        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        ids = (result.get("ids") or [[]])[0]
        documents = (result.get("documents") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]

        hits: list[dict[str, Any]] = []
        for rank, (item_id, document, metadata, distance) in enumerate(
            zip(ids, documents, metadatas, distances),
            start=1,
        ):
            hits.append(
                {
                    "rank": rank,
                    "id": item_id,
                    "text": document,
                    "metadata": metadata or {},
                    "distance": float(distance) if distance is not None else None,
                }
            )

        return hits

    def count(self) -> int:
        return int(self.collection.count())