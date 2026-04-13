from __future__ import annotations

from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer


DEFAULT_EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class FAQEmbedder:
    def __init__(self, model_name: str = DEFAULT_EMBED_MODEL) -> None:
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        if hasattr(self.model, "encode_document"):
            embeddings = self.model.encode_document(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
        else:
            embeddings = self.model.encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )

        return np.asarray(embeddings).tolist()

    def embed_query(self, text: str) -> list[float]:
        clean = (text or "").strip()
        if not clean:
            return []

        if hasattr(self.model, "encode_query"):
            embedding = self.model.encode_query(
                clean,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
        else:
            embedding = self.model.encode(
                clean,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )

        return np.asarray(embedding).tolist()


@lru_cache(maxsize=4)
def get_embedder(model_name: str = DEFAULT_EMBED_MODEL) -> FAQEmbedder:
    return FAQEmbedder(model_name=model_name)