# dialogue prompt
def get_dialogue_prompt():
    prompt = """
    유저의 입력: {user_input}
    
    위 입력에 대해 자연스럽고 친절한 대화체로 응답을 생성해 주세요. 
    유저가 질문을 했으면 그에 대한 답변을, 유저가 인사를 했으면 인사로 응답해 주세요.
    없는 거 지어내지 말고 그냥 아는 것은 일반적 지식 측면에서 대답해 주시고,
    모르는 것은 모른다고 솔직하게 대답해 주세요.
    """
    return prompt