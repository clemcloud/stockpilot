from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models import Product, User # Imported User for type-hinting
from app.schemas.inventory import ProductCreate, ProductResponse
from app.services.inventory_service import get_all_products, get_product_by_id, create_product, update_product

router = APIRouter(prefix="/products", tags=["Products"])


# Public route MUST come before /{product_id}
@router.get("/public", response_model=list[ProductResponse])
def list_products_public(db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.current_stock > 0).all()


@router.get("", response_model=list[ProductResponse])
def list_products(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return get_all_products(db, user_id=current_user.id)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return get_product_by_id(db, product_id=product_id, user_id=current_user.id)


@router.post("", response_model=ProductResponse, status_code=201)
def add_product(
    data: ProductCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return create_product(db, product=data, user_id=current_user.id)


@router.patch("/{product_id}", response_model=ProductResponse)
def edit_product(
    product_id: int, 
    data: ProductCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return update_product(db, product_id=product_id, product_update=data, user_id=current_user.id)