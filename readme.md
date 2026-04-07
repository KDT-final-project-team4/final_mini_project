# 📌 CallFlow Mini – 팀원 공통 과제 안내 (LangGraph 기반)

---

## 🎯 이 과제의 목적

이 과제는 기능을 만드는 것이 아니라,  
다음 5가지를 직접 경험하면서 이해하는 것이 목표다.

- 멀티에이전트 구조가 왜 필요한지
- LangGraph가 왜 필요한지
- state 기반 흐름이 어떻게 작동하는지
- agent와 tool의 역할 차이
- 프론트가 있어도 백엔드 구조가 없으면 왜 의미가 없는지

👉 한 줄 요약: **“챗봇이 아니라 상담 시스템을 직접 만들어보는 과제”**

---

## 📦 해야 할 일 (핵심)

모든 팀원은 아래를 구현해야 한다.

### 1. LangGraph 기반 백엔드 구현
- Intent Router Node
- Dialogue Manager Node
- Tool Nodes
- Response Node

---

### 2. 기존 프론트와 연결
- 새 UI 만들지 않는다
- 제공된 frontend 그대로 사용
- `/chat` API 연결만 한다

---

### 3. 3가지 시나리오 동작시키기
- FAQ
- Callback (이름 → 전화번호)
- Vision Trigger (mock)

---

## 🧠 전체 시스템 구조

```
Frontend UI
    ↓
POST /chat
    ↓
FastAPI
    ↓
LangGraph

Intent Router
    ↓
Dialogue Manager
    ↓
조건 분기
    ├── FAQ Tool
    ├── Callback Tool
    ├── Vision Trigger
    ↓
Response Node
```

---

## 📁 폴더 구조

```
callflow-mini/
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   │
│   └── app/
│       ├── graph.py
│       ├── state.py
│       │
│       ├── nodes/
│       ├── tools/
│       └── prompts/
│
└── frontend/
    └── (이미 만들어진 UI 그대로 사용)
```

---

## 🚨 가장 중요한 규칙

### ❌ 절대 하지 말 것
- 프론트 새로 만들기
- OCR 붙이기
- 이미지 분석 구현
- DB 연결
- 인증 구현
- 복잡하게 만들기

---

### ✅ 반드시 할 것
- LangGraph 사용
- state 기반 흐름 구현
- node / tool 역할 분리
- 기존 프론트 연결

---

## 🧩 반드시 구현해야 하는 구성

---

### 1️⃣ State

```python
state = {
  "user_input": "",
  "intent": None,
  "next_action": None,
  "collected_name": None,
  "collected_phone": None,
  "tool_result": None,
  "final_response": None
}
```

---

### 2️⃣ Intent Router Node

입력 문장을 아래 3개 중 하나로 분류:

- faq
- callback
- unknown

---

### 3️⃣ Dialogue Manager Node

현재 state를 보고 다음 행동 결정:

- faq → FAQ Tool
- callback → 이름/전화번호 수집
- unknown → Vision Trigger

---

### 4️⃣ Tool

#### FAQ Tool
```
운영시간 → 운영시간은 09:00~18:00 입니다
```

#### Callback Tool
```
홍길동 + 전화번호 → 콜백 등록 완료
```

#### Vision Tool (mock)
```
사진을 보내주세요
```

---

### 5️⃣ Response Node

최종 사용자 응답 생성

---

## 💬 반드시 동작해야 하는 시나리오

---

### ✅ 1. FAQ

```
입력: 운영시간 알려줘
출력: 운영시간은 09:00~18:00 입니다
```

---

### ✅ 2. Callback

```
입력: 상담원 연결해줘
→ 이름 입력 요청
→ 전화번호 입력 요청
→ 콜백 등록 완료
```

---

### ✅ 3. Vision

```
입력: 이거 이상해요
출력: 사진을 보내주세요 (mock)
```

---

## 🌐 프론트 연결 방법

프론트는 이미 만들어져 있음.

👉 너가 해야 할 것:

### JS에서 API 호출

```
fetch("http://localhost:8000/chat", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({ message: userInput })
})
```

---

## ⚙️ 실행 방법

### 1. 프로젝트 생성
```
python setup_project.py
```

### 2. 백엔드 실행
```
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## 🧠 과제 완료 기준

다음 질문에 답할 수 있으면 완료다:

---

### 1. 왜 LangGraph를 썼는가?
---

### 2. 왜 Intent Router가 필요한가?
---

### 3. 왜 Dialogue Manager가 따로 있는가?
---

### 4. 왜 Tool로 분리했는가?
---

### 5. 왜 Vision이 fallback인가?
---

## 🔥 가장 중요한 깨달음

이 과제를 하고 나면 반드시 이 생각이 들어야 한다:

- “아, LLM 하나로 다 하면 안 되는구나”
- “상태를 보고 다음 행동을 결정해야 하는구나”
- “그래서 이게 시스템이구나”

---

## 📌 최종 한 줄

👉 **“우리는 챗봇을 만드는 게 아니라 상담 흐름을 만드는 것이다”**