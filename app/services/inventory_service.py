from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models import Product, InventoryLog
from app.schemas import inventory


def get_all_products(db: Session, user_id: int):
    return db.query(Product).filter(Product.owner_id == user_id).all()


def get_product_by_id(db: Session, product_id: int, user_id: int):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.owner_id == user_id
    ).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} does not exist or access denied."
        )
    return product


def create_product(db: Session, product: inventory.ProductCreate, user_id: int):
    db_product = Product(
        name=product.name,
        sku=product.sku,
        description=product.description,
        price=product.price,
        current_stock=product.current_stock,
        min_stock_level=product.min_stock_level,
        owner_id=user_id
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def create_inventory_log(db: Session, log: inventory.InventoryLogCreate, user_id: int):
    product = db.query(Product).filter(
        Product.id == log.product_id,
        Product.owner_id == user_id
    ).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {log.product_id} does not exist or access denied."
        )

    if log.log_type == "removal" and product.current_stock < log.change_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not enough stock for {product.name}. Available: {product.current_stock}"
        )

    if log.log_type == "addition":
        product.current_stock += log.change_amount
    elif log.log_type == "removal":
        product.current_stock -= log.change_amount

    db_log = InventoryLog(
        product_id=log.product_id,
        change_amount=log.change_amount,
        log_type=log.log_type,
        notes=log.notes
    )

    try:
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record inventory log."
        )


def update_product(
    db: Session,
    product_id: int,
    product_update: inventory.productUpdate,
    user_id: int
):
    db_product = db.query(Product).filter(
        Product.id == product_id,
        Product.owner_id == user_id
    ).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found or access denied."
        )

    if product_update.name is not None:
        db_product.name = product_update.name
    if product_update.sku is not None:
        db_product.sku = product_update.sku
    if product_update.description is not None:
        db_product.description = product_update.description
    if product_update.price is not None:
        db_product.price = product_update.price
    if product_update.current_stock is not None:
        db_product.current_stock = product_update.current_stock
    if product_update.min_stock_level is not None:
        db_product.min_stock_level = product_update.min_stock_level

    db.commit()
    db.refresh(db_product)
    return db_product