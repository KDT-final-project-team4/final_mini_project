from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


# --------------------------------------------------------------
# .env 로드
# --------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


# --------------------------------------------------------------
# 기본 앱 설정
# --------------------------------------------------------------
APP_NAME = os.getenv("APP_NAME", "CallFlow Mini Backend")
APP_ENV = os.getenv("APP_ENV", "development")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"


# --------------------------------------------------------------
# OpenAI / LLM 공통 설정
# --------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# 기존 하위호환용 기본 모델
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# --------------------------------------------------------------
# 역할별 모델 설정
# --------------------------------------------------------------
# Intent Router:
# - 짧은 입력
# - 분류 중심
# - 비용/속도 우선
INTENT_ROUTER_MODEL = os.getenv("INTENT_ROUTER_MODEL", OPENAI_MODEL)

# Dialogue Manager:
# - 상태 기반 흐름 결정
# - 상대적으로 짧지만 중요도 높음
DIALOGUE_MANAGER_MODEL = os.getenv("DIALOGUE_MANAGER_MODEL", OPENAI_MODEL)

# Response Node:
# - 사용자 체감 품질에 가장 직접적 영향
# - 자연스러운 응답 생성용
RESPONSE_MODEL = os.getenv("RESPONSE_MODEL", OPENAI_MODEL)

# Evidence Check:
# - 지금은 rule-based라도, 나중에 LLM 판정 붙일 수 있으므로 미리 분리
EVIDENCE_CHECK_MODEL = os.getenv("EVIDENCE_CHECK_MODEL", OPENAI_MODEL)

# 향후 Gemma 4 같은 비교 모델 이름을 넣기 위한 별도 필드
# 예:
#   EXPERIMENT_MODEL=gemma-4
EXPERIMENT_MODEL = os.getenv("EXPERIMENT_MODEL", "")


# --------------------------------------------------------------
# RAG / Embedding / Chroma 설정
# --------------------------------------------------------------
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "callflow_knowledge")
CHROMA_PERSIST_DIRECTORY = os.getenv(
    "CHROMA_PERSIST_DIRECTORY",
    str(BASE_DIR / "data" / "chroma"),
)


# --------------------------------------------------------------
# Retrieval / Evidence 기본 파라미터
# --------------------------------------------------------------
RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "4"))
RETRIEVAL_SCORE_THRESHOLD = float(os.getenv("RETRIEVAL_SCORE_THRESHOLD", "0.15"))

# Evidence Check에서 강한 근거 / 보통 근거 판단 시 참고할 수 있는 기준
EVIDENCE_STRONG_THRESHOLD = float(os.getenv("EVIDENCE_STRONG_THRESHOLD", "0.35"))
EVIDENCE_MODERATE_THRESHOLD = float(os.getenv("EVIDENCE_MODERATE_THRESHOLD", "0.18"))


# --------------------------------------------------------------
# Session / Tenant 기본 설정
# --------------------------------------------------------------
DEFAULT_TENANT_ID = os.getenv("DEFAULT_TENANT_ID", "default")


# --------------------------------------------------------------
# Callback / Action 관련 설정
# --------------------------------------------------------------
MAX_NAME_RETRY = int(os.getenv("MAX_NAME_RETRY", "2"))
MAX_PHONE_RETRY = int(os.getenv("MAX_PHONE_RETRY", "2"))


# --------------------------------------------------------------
# Logging / Debug 설정
# --------------------------------------------------------------
ENABLE_DEBUG_INFO = os.getenv("ENABLE_DEBUG_INFO", "true").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


# --------------------------------------------------------------
# 모델 선택 헬퍼
# --------------------------------------------------------------
def get_router_model() -> str:
    """
    Intent Router에서 사용할 모델명 반환.
    """
    return INTENT_ROUTER_MODEL


def get_dialogue_manager_model() -> str:
    """
    Dialogue Manager에서 사용할 모델명 반환.
    """
    return DIALOGUE_MANAGER_MODEL


def get_response_model() -> str:
    """
    Response Node에서 사용할 모델명 반환.
    """
    return RESPONSE_MODEL


def get_evidence_check_model() -> str:
    """
    Evidence Check에서 사용할 모델명 반환.
    현재는 rule-based여도 향후 대비용으로 유지한다.
    """
    return EVIDENCE_CHECK_MODEL


def get_experiment_model_or_default(default_model: str) -> str:
    """
    실험용 모델(EXPERIMENT_MODEL)이 설정되어 있으면 우선 사용하고,
    없으면 default_model을 그대로 반환한다.

    사용 예:
        model_name = get_experiment_model_or_default(get_router_model())
    """
    return EXPERIMENT_MODEL or default_model