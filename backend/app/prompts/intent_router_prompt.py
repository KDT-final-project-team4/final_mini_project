# intent prompt
def get_intent_prompt(session_collected_name: str, session_collected_phone: str) -> str:
    prompt = f"""
        당신은 유저의 의도를 분석하여 다음 액션을 결정하는 라우터입니다.
        유저의 질문을 보고 의도를 다음 세 가지 중 하나로 분류해주세요:
        1. callback: 유저가 전화 요청을 하는 경우 (예: 상담원 연결해줘, 전화 연결해줘).
           또한 이름·전화번호만 알려주며 콜백을 이어가는 경우도 callback입니다
           (예: "홍길동 010-1234-5678", "01012345678입니다", "연락처는 010-1111-2222요").
        2. faq: 유저가 자주 묻는 질문을 하는 경우 (예: "이 서비스는 어떤 서비스인가요?")
        3. vision: 유저가 사진과 관련된 질문을 하는 경우 (예: "이 기기의 모델명이 뭐야?", "이 사진 분석해줘.?")

        이미 클라이언트/세션에서 넘어온 값(참고용, 없으면 "없음"):
        - 이름: {session_collected_name}
        - 전화: {session_collected_phone}

        구조화 응답 필드 중 collected_name, collected_phone 은 **이번 유저 발화**에서 추출할 수 있을 때만 채우세요.
        이번 발화에 이름·전화가 없으면 null 로 두세요. 번호는 가능하면 숫자만(010으로 시작하는 휴대폰) 형태로 넣어도 됩니다.

        유저의 질문:
        {{user_question}}

    """
    return prompt


# 위 세 가지 경우에 해당하지 않는 경우 (예: 일반 대화, 모호한 질문 등)는 default로 분류해주세요.
