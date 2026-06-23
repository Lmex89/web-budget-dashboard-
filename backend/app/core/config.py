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

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]

    # Cookies
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
