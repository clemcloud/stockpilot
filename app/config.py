from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App Configuration
    APP_NAME: str = "StockPilot"
    DEBUG: bool = True
    
    # Production-Ready Database (Read directly from your .env)
    DATABASE_URL: str
    
    # Security & Tokens
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # AWS Predictive Layer
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "us-west-1"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()