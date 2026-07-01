from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models import Product, InventoryLog
from app.schemas import inventory

def get_all_products(db: Session):
    return db.query(Product).all()

def get_product_by_id(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} does not exist."
        )
    return product

def create_product(db: Session, product: inventory.ProductCreate):
    db_product = Product(
        name=product.name,
        sku=product.sku,
        description=product.description,
        price=product.price,
        current_stock=product.current_stock,
        min_stock_level=product.min_stock_level
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def create_inventory_log(db: Session, log: inventory.InventoryLogCreate):
    # 1. Verify the product exists before doing anything
    product = db.query(Product).filter(Product.id == log.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cannot log inventory. Product with ID {log.product_id} does not exist."
        )

    # 2. Prevent stock from dropping below zero during manual removal
    if log.log_type == "removal" and product.current_stock < log.change_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Incomplete removal: Not enough stock for {product.name}. Available: {product.current_stock}"
        )

    # 3. Adjust the stock values
    if log.log_type == "addition":
        product.current_stock += log.change_amount
    elif log.log_type == "removal":
        product.current_stock -= log.change_amount

    # 4. Initialize the log entry
    db_log = InventoryLog(
        product_id=log.product_id,
        change_amount=log.change_amount,
        log_type=log.log_type,
        notes=log.notes
    )
    
    # 5. Save everything in ONE clean database transaction
    try:
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record inventory log adjustment."
        )

def update_product(db: Session, product_id: int, product_update: inventory.productUpdate):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cannot update. Product with ID {product_id} not found."
        )
        
    db_product.name = product_update.name
    db_product.sku = product_update.sku
    db_product.description = product_update.description
    db_product.price = product_update.price
    db_product.current_stock = product_update.current_stock
    db_product.min_stock_level = product_update.min_stock_level
    
    db.commit()
    db.refresh(db_product)
    return db_product