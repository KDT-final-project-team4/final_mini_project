from app.tools.callback_tool import callback_tool

# callback_node node
def run(state):

    name = state.get('collected_name', 'admin')
    phone = state.get('collected_phone', '01012345678')

    if name and phone:
        callback = callback_tool(name, phone)

    return {
        'tool_result': callback,
        'collected_name': name,
        'collected_phone': phone,
    }
