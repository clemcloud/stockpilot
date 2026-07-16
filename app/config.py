from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # Database
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # AWS
    AWS_REGION: str = "us-east-1"
    SNS_TOPIC_ARN: str = ""
    SES_SENDER_EMAIL: str = ""
    S3_BUCKET_NAME: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()