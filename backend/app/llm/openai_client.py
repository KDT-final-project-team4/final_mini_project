from __future__ import annotations

import os

from openai import OpenAI


def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=api_key)


def get_intent_model() -> str:
    return os.getenv("OPENAI_INTENT_MODEL", "gpt-5.4-mini")


def get_response_model() -> str:
    return os.getenv("OPENAI_RESPONSE_MODEL", "gpt-5.4-mini")