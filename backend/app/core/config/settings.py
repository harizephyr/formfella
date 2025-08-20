# settings.py
from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    
    OPENAI_API_KEY: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_DEFAULT_REGION: str
    DB_HOST: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_PORT: str
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_PUBLISHABLE_KEY: str
    class Config:
        env_file = ".env.local"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()

    