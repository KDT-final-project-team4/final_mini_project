from app.graph import build_graph

def run_cli():
    graph = build_graph()

    # 세션처럼 유지할 state
    state = {
        'user_input': '',
        'intent': None,
        'next_action': None,
        'collected_name': None,
        'collected_phone': None,
        'tool_reuslt': None,
        'final_response': None,
    }

    print('=== CallFlow Mini CLI ===')
    print("종료하려면 'exit' 입력\n")

    while True:
        user_input = input('사용자: ').strip()

        if user_input.lower() == 'exit':
            print('종료합니다.')
            break

        # 현재 턴 입력 반영
        state['user_input'] = user_input

        # 그래프 실행
        state = graph.invoke(state)

        # 최종 응답 출력
        print(f"AI: {state.get('final_response')}")

        # callback 흐름에서 이름/전화번호 수집
        if state.get('next_action') == 'ask_name':
            name = input('이름 입력: ').strip()
            state['collected_name'] = name
            phone = input('전화번호 입력: ').strip()
            state['collected_phone'] = phone

            # 이름/전화번호 입력 후 다시 callback 완료 흐름 실행
            state['user_input'] = '콜백 계속 진행'
            state = graph.invoke(state)
            print(f"AI: {state.get('final_response')}")

if __name__ == "__main__":
    run_cli()