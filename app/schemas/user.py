from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


#This is used to create the user to validate it .
class UserCreate(BaseModel):
    email: EmailStr
    
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=20, 
        description="Unique username for the account"
    )
    
    password: str = Field(
        ..., 
        min_length=8, 
        description="Plain-text password, will be hashed by the service layer"
    )


# This is the user response.
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    role: str
    is_active: bool
    created_at: datetime

    # This inner config allows Pydantic to read SQLAlchemy ORM models directly
    class Config:
        from_attributes = True


# ==========================================
# 3. USER UPDATE (INBOUND PATCH CONTRACT)
# ==========================================
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    
    username: Optional[str] = Field(
        None, 
        min_length=3, 
        max_length=20, 
        description="Optional update to username"
    )
    
    password: Optional[str] = Field(
        None, 
        min_length=8, 
        description="Optional password reset"
    )