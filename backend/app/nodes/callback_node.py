from app.tools.callback_tool import callback_tool

# callback_node node
def run(state):

    name = state.get('collected_name')
    phone = state.get('collected_phone')

    if name and phone:
        callback = callback_tool(name, phone)
        state['tool_result'] = callback

    return state
