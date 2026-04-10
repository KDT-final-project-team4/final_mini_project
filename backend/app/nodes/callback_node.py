from app.tools.callback_tool import callback_tool

# callback_node node
def run(state):
    name = state.get("collected_name")
    phone = state.get("collected_phone")

    if isinstance(name, str):
        name = name.strip() or None
    if isinstance(phone, str):
        phone = phone.strip() or None

    callback = None
    if name and phone:
        callback = callback_tool(name, phone)

    return {
        "tool_result": callback,
        "collected_name": name,
        "collected_phone": phone,
    }
