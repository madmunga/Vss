from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_S: str = ""
    STRIPE_PRICE_A: str = ""
    STRIPE_PRICE_B: str = ""

    FRONTEND_URL: str = "http://localhost:5173"

    # Email / SMTP (optional — falls back to console log if not set)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@vss.app"
    SMTP_TLS: bool = True

    @property
    def stripe_price_map(self) -> dict:
        return {"S": self.STRIPE_PRICE_S, "A": self.STRIPE_PRICE_A, "B": self.STRIPE_PRICE_B}

    @property
    def tier_price_usd(self) -> dict:
        return {"S": 50, "A": 30, "B": 10}


settings = Settings()
