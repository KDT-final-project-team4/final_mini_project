# vision_node node
from app.state import CallFlowState

def run(state: CallFlowState) -> CallFlowState:
    """
    Vision Fallback Specialist Agent Node
    - 시각 정보가 필요한 요청을 처리
    - 현재는 mock으로 이미지 업로드 요청 메시지 생성
    - 결과를 tool_result에 저장
    """

    user_input = state.get('user_input', '').strip()

    # 지금은 mock (추후 CV 모델 연결)
    result = '정확한 확인을 위해 사진을 보내주세요.'

    state['tool_result'] = result

    print('[Vision Node]')
    print(' user_input:', user_input)
    print(' tool_result:', result)
    
    return state
