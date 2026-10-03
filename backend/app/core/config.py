import secrets

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "Family Budget API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Production-ready API for family budget management"
    ENVIRONMENT: str = "development"  # development | staging | production

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200

    # Database
    DATABASE_URL: str = "mysql+aiomysql://budget_user:budget_pass@localhost:3306/family_budget"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 3600
    DB_ECHO: bool = False

    # Logging
    LOG_LEVEL: str = "INFO"

    # CORS
    BACKEND_CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Email (provider-agnostic; Brevo is the bundled adapter)
    EMAIL_PROVIDER: str = "disabled"  # disabled | console | brevo
    EMAIL_API_KEY: str = ""  # generic key, preferred
    BREVO_API_KEY: str = ""  # Brevo-specific key
    # Legacy env names kept so existing .env files keep working.
    APIKEY_BREVO: str = ""
    APIKYE_BREVO: str = ""
    EMAIL_FROM_EMAIL: str = ""  # must be a verified sender at the provider
    EMAIL_FROM_NAME: str = "Family Budget"
    APP_BASE_URL: str = ""  # optional frontend URL used for links in emails

    # Multi-tenancy
    # Enables the global SQLAlchemy tenant guard (`with_loader_criteria`) that
    # injects `family_id == <active family>` into every SELECT on tenant-owned
    # models. Defense-in-depth safety net; keep service-level checks regardless.
    ENABLE_GLOBAL_TENANT_GUARD: bool = False

    # Timezone
    TIMEZONE: str = "America/Merida"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def resolved_email_api_key(self) -> str:
        """Return the first configured email API key, generic names first."""
        return self.EMAIL_API_KEY or self.BREVO_API_KEY or self.APIKEY_BREVO or self.APIKYE_BREVO

    # Cookies
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
