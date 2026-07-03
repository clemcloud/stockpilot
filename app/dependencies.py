from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.security import decode_access_token
from app.services.user_service import get_user_by_id

# Points FastAPI to the login URL endpoint for extracting bearer tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db():
    """
    Opens an isolated database connection when a request hits a route,
    and guarantees it closes securely when the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    The security guard checking the visitor badge (JWT):
    1. Intercepts the request and decodes the token using app.security.
    2. Validates the user exists in the database.
    3. Blocks unauthorized or expired sessions immediately.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials, please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 1. Decode the token using your exact utility function
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
        
    # 2. Extract the user ID from the token payload ('sub' claim)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
        
    # 3. Use the database connection to make sure the user account is real
    try:
        user = get_user_by_id(db, user_id=int(user_id))
    except HTTPException:
        raise credentials_exception
        
    return user