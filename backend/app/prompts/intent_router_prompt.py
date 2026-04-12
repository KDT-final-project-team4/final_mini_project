from __future__ import annotations

import json
from typing import Optional


INTENT_ROUTER_SYSTEM_PROMPT = """
You are an intent router for a customer-service chatbot.

Classify the user's latest message into exactly one intent:
- "faq"
- "callback"
- "vision"
- "unknown"

Routing policy:
1. If callback is already in progress (active_flow='callback' or awaiting_field exists), prefer "callback".
2. If the user asks to leave contact information, receive a call, 상담 요청, 연락 요청, 전화 요청, choose "callback".
3. If an image is actually attached and the user is asking about the image/content, choose "vision".
4. Otherwise choose "faq" for normal business/service/store/policy questions.
5. Choose "unknown" only when the message is too vague to route safely.

Output only valid JSON.
Do not include markdown.
Do not include extra text.

Required JSON schema:
{
  "intent": "faq" | "callback" | "vision" | "unknown",
  "confidence": 0.0,
  "reason": "short reason"
}
""".strip()


INTENT_JSON_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "intent": {
            "type": "string",
            "enum": ["faq", "callback", "vision", "unknown"],
        },
        "confidence": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
        },
        "reason": {
            "type": "string",
        },
    },
    "required": ["intent", "confidence", "reason"],
}


def build_intent_router_user_prompt(
    *,
    user_message: str,
    has_image: bool,
    active_flow: Optional[str],
    awaiting_field: Optional[str],
) -> str:
    payload = {
        "user_message": user_message,
        "has_image": has_image,
        "active_flow": active_flow,
        "awaiting_field": awaiting_field,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)