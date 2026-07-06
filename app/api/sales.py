from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.sales import SaleCreate, SaleResponse
from app.services.sales import create_sale_transaction, get_all_sales, get_sale_by_id
from app.models import User # Imported the User model so we can type-hint the dependency

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.post("", response_model=SaleResponse, status_code=201)
def process_sale(data: SaleCreate, db: Session = Depends(get_db)):
    # No auth on purpose — POS terminal is public. 
    # Passing user_id=1 as a baseline fallback since the service now requires it.
    return create_sale_transaction(db, data, user_id=1)


@router.get("", response_model=list[SaleResponse])
def list_sales(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user) # 1. Changed '_' to 'current_user'
):
    # 2. Passed the tracking key down to the query execution rule
    return get_all_sales(db, user_id=current_user.id)


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user) # 1. Changed '_' to 'current_user'
):
    # 2. Passed the user ID to ensure they can only view their own sales
    return get_sale_by_id(db, sale_id=sale_id, user_id=current_user.id)