from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.sales import SaleCreate, SaleResponse
from app.services.sales import (
    create_sale_transaction,
    get_all_sales,
    get_sale_by_id,
)
from app.models import User

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.post("", response_model=SaleResponse, status_code=201)
def process_sale(data: SaleCreate, db: Session = Depends(get_db)):
    return create_sale_transaction(db, data, user_id=data.owner_id)


@router.get("", response_model=list[SaleResponse])
def list_sales(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_sales(db, user_id=current_user.id)


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_sale_by_id(db, sale_id=sale_id, user_id=current_user.id)