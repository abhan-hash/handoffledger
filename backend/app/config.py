"""
Application Configuration
"""

import os
from typing import List
from pydantic import BaseModel, Field


class Settings(BaseModel):
    PROJECT_NAME: str = "HandoffLedger"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = Field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./handoff_ledger.db"))
    OPENAI_API_KEY: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    NVIDIA_API_KEY: str = Field(default_factory=lambda: os.getenv("NVIDIA_API_KEY", os.getenv("NEMOTRON_API_KEY", "")))
    NVIDIA_BASE_URL: str = Field(default_factory=lambda: os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"))
    NVIDIA_MODEL: str = Field(default_factory=lambda: os.getenv("NVIDIA_MODEL", "nvidia/nemotron-3-ultra-550b-a55b"))
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
    DEFAULT_LEAVER_NAME: str = Field(default_factory=lambda: os.getenv("DEFAULT_LEAVER_NAME", "Alice Maintainer"))
    CANARY_TOKEN_SEED: str = Field(default_factory=lambda: os.getenv("CANARY_TOKEN_SEED", "CANARY_SECRET_UUIDv4_9823f4b1"))

    @property
    def has_nvidia_key(self) -> bool:
        return bool(self.NVIDIA_API_KEY and len(self.NVIDIA_API_KEY.strip()) > 5)


settings = Settings()
