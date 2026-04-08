# response_node node

def run(state):

    if tool_result := state.get('tool_result'):
        state['final_response'] = tool_result
        
    return state
