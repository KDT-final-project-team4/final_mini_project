from app.tools.callback_tool import callback_tool


# callback_node node
def run(state):
    name = state.get("collected_name")
    phone = state.get("collected_phone")

    if name and phone:
        return {
            "collected_name": name,
            "collected_phone": phone,
            "tool_result": callback_tool(name, phone),
        }
    else:
        return {
            "collected_name": name if name else None,
            "collected_phone": phone if phone else None,
            "tool_result": None,
        }
