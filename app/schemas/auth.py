from pydantic import BaseModel
from typing import Optional


class LoginSchema(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str


class TokenData(BaseModel):
    username: Optional[str] = None