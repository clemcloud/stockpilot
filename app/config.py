from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    #The first is the database url to contain our database access credentials.


    DATABASE_URL: str 

    # The second is the jwt tokens , that is used for the authentication of the warehouse manager.


    SECRET_KEY: str 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()