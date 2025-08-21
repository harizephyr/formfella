# settings.py
from pydantic_settings import BaseSettings
from app.services.aws_services import get_secret

secrets = get_secret()
class Settings(BaseSettings):
    
    OPENAI_API_KEY: str = secrets['OPENAI_API_KEY']
    AWS_ACCESS_KEY_ID: str = secrets['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY: str = secrets['AWS_SECRET_ACCESS_KEY']
    AWS_DEFAULT_REGION: str = secrets['AWS_DEFAULT_REGION']
    DB_HOST: str = secrets['DB_HOST']
    DB_USER: str = secrets['DB_USER']
    DB_PASSWORD: str = secrets['DB_PASSWORD']
    DB_NAME: str = secrets['DB_NAME']
    DB_PORT: str = secrets['DB_PORT']
    STRIPE_SECRET_KEY: str = secrets['STRIPE_SECRET_KEY']
    STRIPE_WEBHOOK_SECRET: str = secrets['STRIPE_WEBHOOK_SECRET']
    STRIPE_PUBLISHABLE_KEY: str = secrets['STRIPE_PUBLISHABLE_KEY']
    COGNITO_USER_POOL_ID: str = secrets['COGNITO_USER_POOL_ID']
    COGNITO_CLIENT_ID: str = secrets['COGNITO_CLIENT_ID']
    COGNITO_CLIENT_SECRET: str = secrets['COGNITO_CLIENT_SECRET']
    class Config:
        env_file = ".env.local"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()

    