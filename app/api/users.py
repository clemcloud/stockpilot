from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.user_service import create_user, get_user_by_id, update_user_profile

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserResponse, status_code=201)
def register_user(data: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, data)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)  # Removed strict Pydantic type-hint
):
    return get_user_by_id(db, user_id)


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int, 
    data: UserUpdate, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)  # Aligned to ensure Swagger enforces authorization
):
    return update_user_profile(db, user_id, data)