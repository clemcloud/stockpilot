from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel  # We use this to build schemas right here

from app.database import get_db
from app.security import create_access_token, verify_password
from app.services.user_service import get_user_by_username

# 1. DEFINE YOUR SCHEMAS INLINE (Fixes the missing schemas.auth file error)
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"  # Standard OAuth2 requirement

# 2. SETUP THE ROUTER WING
router = APIRouter(prefix="/auth", tags=["Auth"])


# 3. THE LOGIN ENDPOINT
@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    # Look up user in the database
    user = get_user_by_username(db, data.username)
    
    # Check if user exists and verify their password using your security.py helper
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Generate the signed JWT using your security.py helper
    token = create_access_token(data={"sub": str(user.id), "role": user.role})
    
    # Return data matching the TokenResponse structure exactly
    return {"access_token": token, "token_type": "bearer"}