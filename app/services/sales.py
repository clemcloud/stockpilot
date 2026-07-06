from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import Sale, SalesItem, Product
from app.schemas.sales import SaleCreate 
from datetime import datetime
import uuid

def create_sale_transaction(db: Session, sale_data: SaleCreate, user_id: int) -> Sale:
    receipt_number = f"REC-{str(uuid.uuid4()).upper()[:8]}"
    total_amount = 0.0
    sales_items_to_create = []

    for item in sale_data.items:
        # Secure Check: Ensure the target product belongs to the user checking out
        product = db.query(Product).filter(Product.id == item.product_id, Product.owner_id == user_id).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {item.product_id} does not exist or access denied."
            )
            
        if product.current_stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.name}. Available: {product.current_stock}, Requested: {item.quantity}"
            )
            
        current_unit_price = product.price
        total_amount += current_unit_price * item.quantity
        product.current_stock -= item.quantity
        
        db_sales_item = SalesItem(
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=current_unit_price
        )
        sales_items_to_create.append(db_sales_item)

    # FIX: Explicitly pass owner_id to the base Sale schema node
    db_sale = Sale(
        receipt_number=receipt_number,
        total_amount=total_amount,
        payment_method=sale_data.payment_method,
        timestamp=datetime.utcnow(),
        owner_id=user_id  # Ties ledger row strictly to this administrator
    )
    
    db_sale.sales_items = sales_items_to_create

    try:
        db.add(db_sale)
        db.commit()
        db.refresh(db_sale)
        return db_sale
    except Exception:
        db.rollback() 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the sales transaction."
        )

# FIX: Scope transaction retrieval lists strictly by identity
def get_all_sales(db: Session, user_id: int):
    return db.query(Sale).filter(Sale.owner_id == user_id).all()

# FIX: Validate authorization permissions before pulling historical records
def get_sale_by_id(db: Session, sale_id: int, user_id: int):
    sale = db.query(Sale).filter(Sale.id == sale_id, Sale.owner_id == user_id).first()
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sale transaction with ID {sale_id} not found or access denied."
        )
    return sale