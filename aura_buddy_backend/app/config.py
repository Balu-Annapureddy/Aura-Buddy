from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database — defaults to SQLite for local dev; set to PostgreSQL in .env for production
    DATABASE_URL: str = "sqlite:///./aura_buddy.db"

    # Firebase
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None

    # Aura Economy
    AD_REWARD_AMOUNT: int = 100
    AD_REWARD_MAX_CLAIMS: int = 2
    AD_REWARD_WINDOW_HOURS: int = 12
    PREMIUM_MONTHLY_BONUS: int = 1000
    DAILY_POST_LIMIT_STANDARD: int = 3
    DAILY_POST_LIMIT_PREMIUM: int = 4
    MISSION_APPROVAL_THRESHOLD: int = 5
    MISSION_REJECTION_THRESHOLD: int = 5
    MISSION_REWARD_AMOUNT: int = 200

    # App
    APP_NAME: str = "Aura Buddy"
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
