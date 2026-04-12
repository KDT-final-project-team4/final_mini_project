from __future__ import annotations

import logging
import os
from dataclasses import dataclass


def _to_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Settings:
    APP_ENV: str
    DEBUG_LOG: bool
    LOG_LEVEL: str

    FAQ_MODE: str          # mock | llm | rag
    CALLBACK_MODE: str     # mock | llm
    VISION_MODE: str       # mock | llm

    UNKNOWN_FALLBACK: str  # reply | vision

    CORS_ORIGINS: list[str]


def load_settings() -> Settings:
    cors_raw = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000",
    )

    return Settings(
        APP_ENV=os.getenv("APP_ENV", "dev"),
        DEBUG_LOG=_to_bool(os.getenv("DEBUG_LOG"), True),
        LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO").upper(),
        FAQ_MODE=os.getenv("FAQ_MODE", "mock").lower(),
        CALLBACK_MODE=os.getenv("CALLBACK_MODE", "mock").lower(),
        VISION_MODE=os.getenv("VISION_MODE", "mock").lower(),
        UNKNOWN_FALLBACK=os.getenv("UNKNOWN_FALLBACK", "reply").lower(),
        CORS_ORIGINS=[origin.strip() for origin in cors_raw.split(",") if origin.strip()],
    )


settings = load_settings()


def configure_logging() -> None:
    level_name = settings.LOG_LEVEL if settings.DEBUG_LOG else "WARNING"
    level = getattr(logging, level_name, logging.INFO)

    root_logger = logging.getLogger()
    if root_logger.handlers:
        root_logger.setLevel(level)
        return

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)