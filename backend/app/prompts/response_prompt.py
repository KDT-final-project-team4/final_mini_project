from __future__ import annotations

import json
from typing import Any, Optional


RESPONSE_SYSTEM_PROMPT = """
You generate the final chatbot response.

Hard rules:
1. Use only the provided grounded data.
2. Do not invent facts such as hours, prices, policies, addresses, promises, or unavailable services.
3. If grounded data is insufficient, say you cannot confirm that information.
4. Keep the answer concise and natural.
5. For callback:
   - Ask only for the missing field.
   - If awaiting_field is "name", ask for the name only.
   - If awaiting_field is "phone", ask for the phone number only.
   - If callback is complete, confirm the request was received.
6. For vision:
   - If analysis is uncertain, clearly say the image is not clear enough.
""".strip()


def build_response_user_prompt(
    *,
    user_message: str,
    intent: str,
    awaiting_field: Optional[str],
    tool_output: Optional[dict[str, Any]],
) -> str:
    payload = {
        "user_message": user_message,
        "intent": intent,
        "awaiting_field": awaiting_field,
        "tool_output": tool_output,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)