import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Google Gemini API
    GEMINI_API_KEY: str

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000"

    # MySQL Configuration
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "chatbot_db"

    # MySQL Connection Pool
    MYSQL_POOL_SIZE: int = 5
    MYSQL_POOL_NAME: str = "chatbot_pool"
    MYSQL_POOL_RESET_SESSION: bool = True

    # Application Settings
    APP_NAME: str = "Zyntra AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Server Configuration
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    RELOAD: bool = True

    # Session Configuration
    SESSION_TIMEOUT_MINUTES: int = 30
    MAX_SESSIONS_PER_USER: int = 10

    # Default User ID
    DEFAULT_USER_ID: str = "default_user"

    class Config:
        env_file = ".env"


settings = Settings()
os.environ["GEMINI_API_KEY"] = settings.GEMINI_API_KEY