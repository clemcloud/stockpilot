from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password

def get_user_by_id(db: Session, user_id: int):
    """Fetches a user record by their unique database ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} does not exist."
        )
    return user


def get_user_by_username(db: Session, username: str):
    """Fetches a user record by their unique username for the login flow."""
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user_data: UserCreate):
    """
    Registers a new user matching your UserCreate schema inputs.
    """
    # 1. Check for duplicate username
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this username already exists."
        )

    # 2. Check for duplicate email
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )

    # 3. Save with fields from schema + a default role
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role="manager"  # Defaulting role since it's not in UserCreate schema
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the account."
        )


def update_user_profile(db: Session, user_id: int, update_data: UserUpdate):
    """
    Updates user attributes dynamically. Safe for Optional schema inputs.
    """
    db_user = get_user_by_id(db, user_id)
    
    # 1. Update username conditionally (only if provided and changed)
    if update_data.username is not None and update_data.username != db_user.username:
        if db.query(User).filter(User.username == update_data.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This username is already taken."
            )
        db_user.username = update_data.username
    
    # 2. Update email conditionally (only if provided and changed)
    if update_data.email is not None and update_data.email != db_user.email:
        if db.query(User).filter(User.email == update_data.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This email address is already in use by another account."
            )
        db_user.email = update_data.email
    
    # 3. Handle password change safely (only if provided)
    if update_data.password is not None:
        db_user.hashed_password = hash_password(update_data.password)
        
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile information."
        )