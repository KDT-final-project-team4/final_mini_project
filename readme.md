# 🚀 CallFlow Mini (LangGraph 기반 멀티에이전트 상담 시스템)

---

## 📌 프로젝트 개요

이 프로젝트는 **AI 기반 상담 시스템(CallFlow)**의 축소판(mini version)을 구현한 것이다.

단순한 챗봇이 아니라 다음과 같은 구조를 가진다:

- 🔹 멀티에이전트 구조 (역할 분리)
- 🔹 LangGraph 기반 흐름 제어
- 🔹 상태(state) 기반 의사결정
- 🔹 Tool 호출 구조
- 🔹 Vision fallback (mock)

👉 목표:  
**“챗봇이 아니라 상담 시스템을 이해하는 것”**

---

## 🧠 전체 구조

```
Frontend UI
    ↓
POST /chat API
    ↓
FastAPI Backend
    ↓
LangGraph Flow
    ├── Intent Router
    ├── Dialogue Manager
    ├── Tool Nodes
    │     ├── FAQ
    │     ├── Callback
    │     └── Vision (mock)
    └── Response Node
    ↓
응답 반환
```

---

## 📦 폴더 구조

```
callflow-mini/
│
├── backend/
│   ├── main.py              # FastAPI 서버
│   ├── requirements.txt
│   │
│   └── app/
│       ├── graph.py         # LangGraph 정의
│       ├── state.py         # 상태 정의
│       │
│       ├── nodes/           # Agent 역할
│       ├── tools/           # 실행 함수
│       └── prompts/         # LLM 프롬프트
│
├── frontend/
│   └── (기존 UI 그대로 사용)
│
└── setup_project.py         # 프로젝트 자동 생성 스크립트
```

---

## 🎯 핵심 개념

### 1️⃣ Agent vs Tool

| 구분 | 역할 |
|------|------|
| Agent (Node) | 판단 |
| Tool | 실행 |

👉 예:
- Intent Router → 분류
- Dialogue Manager → 다음 행동 결정
- FAQ Tool → 실제 데이터 반환

---

### 2️⃣ State 기반 흐름

모든 노드는 `state`를 공유한다.

예시:

```
{
  "user_input": "운영시간 알려줘",
  "intent": "faq",
  "next_action": "call_faq",
  "tool_result": "운영시간은 09:00~18:00 입니다."
}
```

👉 핵심:
- 노드는 state를 읽고 수정한다
- 다음 노드는 수정된 state를 기반으로 동작한다

---

## 🧩 구현된 기능

### ✅ 1. FAQ
- 질문 → 답변 반환

예:
```
운영시간 알려줘
→ 운영시간은 09:00~18:00 입니다
```

---

### ✅ 2. Callback (다단계 흐름)

```
상담원 연결해줘
→ 이름 요청
→ 전화번호 요청
→ 콜백 등록 완료
```

---

### ✅ 3. Vision Trigger (Fallback)

```
이거 이상해요
→ 사진을 보내주세요 (mock)
```

👉 실제 Vision은 구현하지 않고 구조만 반영

---

## ⚙️ 설치 및 실행

### 1. 프로젝트 생성

```
python setup_project.py
```

---

### 2. 백엔드 실행

```
cd callflow-mini/backend
pip install -r requirements.txt
uvicorn main:app --reload
```

---

### 3. API 테스트

```
curl -X POST http://127.0.0.1:8000/chat \
-H "Content-Type: application/json" \
-d '{"message":"운영시간 알려줘"}'
```

---

### 4. 프론트 연결

frontend 폴더는 기존 UI를 그대로 사용한다.

JS에서 아래처럼 API 연결:

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

## 🚨 제한 사항

### ❌ 하지 말 것
- 실제 OCR 구현
- 실제 이미지 분석
- DB 연결
- 인증 시스템 구현
- 프론트 재구성

### ✅ 반드시 할 것
- LangGraph 사용
- state 기반 흐름
- node / tool 분리
- 기존 프론트 연동

---

## 🧠 이 프로젝트의 핵심

👉 이건 챗봇이 아니다

👉 **상담 흐름을 가진 시스템이다**

---

## 🔥 왜 중요한가

이 구조를 이해하면:

- 단순 GPT 호출 → ❌
- 시스템 설계 → ⭕

즉,

👉 “LLM을 쓰는 개발자”에서  
👉 “AI 시스템을 설계하는 개발자”로 넘어간다

---

## 📌 최종 한 줄

👉 **“UI는 껍데기고, LangGraph가 뇌다”**