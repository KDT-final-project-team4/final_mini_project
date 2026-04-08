from app.tools.vision_tool import vision_tool 

# vision_node node

def run(state):
    return_message = vision_tool()
    return {
        'tool_result': return_message
    }
