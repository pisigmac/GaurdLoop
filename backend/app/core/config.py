import os
from functools import lru_cache
from typing import List

class Settings:
    PROJECT_NAME: str = "GuardLoop"
    VERSION: str = "1.0.0"
    ENV: str = os.getenv("ENV", "development")

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://guardloop:guardloop@postgres:5432/guardloop"
    )

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "guardloop-dev-secret-change-in-prod")
    CLERK_JWKS_URL: str = os.getenv(
        "CLERK_JWKS_URL",
        "https://clerk.guardloop.dev/.well-known/jwks.json"
    )

    # Scoring weights (configurable per org)
    DEFAULT_TEST_WEIGHT: float = 0.40
    DEFAULT_COVERAGE_WEIGHT: float = 0.25
    DEFAULT_SECURITY_WEIGHT: float = 0.20
    DEFAULT_BEHAVIORAL_WEIGHT: float = 0.15

    # Thresholds
    AUTO_APPROVE_THRESHOLD: int = 90
    HUMAN_REVIEW_THRESHOLD: int = 70
    BLOCK_THRESHOLD: int = 50

    # Browser verify
    PLAYWRIGHT_TIMEOUT: int = 30000
    BROWSER_VERIFY_POOL_SIZE: int = 5

    # Loop monitor
    MAX_LOOP_ITERATIONS: int = 50
    CONTEXT_BLOAT_THRESHOLD: int = 8000  # tokens
    DRIFT_SIMILARITY_THRESHOLD: float = 0.85

    # PII
    PII_ENTITY_TYPES: List[str] = [
        "PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "CREDIT_CARD",
        "US_SSN", "US_PASSPORT", "IBAN", "CRYPTO", "IP_ADDRESS"
    ]

    # Agents
    SUPPORTED_AGENTS: List[str] = ["cursor", "claude_code", "github_copilot", "openai_codex", "aider", "continue_dev", "windsurf", "devin", "custom"]

    # Webhooks
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "whsec_dev")

    # Stripe
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    # Monitoring
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")

    @property
    def is_production(self) -> bool:
        return self.ENV == "production"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
