# response prompt
def get_response_prompt():
    prompt = """
    유저의 입력: {user_input}
    유저의 의도: {intent}
    도구 실행 결과: {tool_result}
    
    위 정보를 바탕으로 최종 사용자 응답을 생성해 주세요. 
    intent가 default인 경우 그냥 일반 지식 수준에서 응답을 만들어 주세요. 모르겠다면 모른다고 솔직하게 답변해 주세요.
    도구 실행 결과가 있다면 그것을 활용해서 응답을 풍부하게 만들어 주세요.
    """
    return prompt