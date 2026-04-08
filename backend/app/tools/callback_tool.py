class CallbackExemples:
    def __init__(self, name, phone):
        self.name = name
        self.phone = phone


def callback_tool(name, phone):
    example = CallbackExemples(name, phone)
    return f"{example.name}님 콜백 등록 완료"
