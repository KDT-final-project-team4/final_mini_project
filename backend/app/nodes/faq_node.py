from app.tools.faq_tool import faq_tool


# faq_node node
def run(state):
    message = state.get('user_input')
    resp = faq_tool(message)
    return {
        'tool_result': resp
    }