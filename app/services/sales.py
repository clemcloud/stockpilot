from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import Sale, SalesItem, Product
from app.schemas.sales import SaleCreate  # Adjust based on your exact schema filename
from datetime import datetime
import uuid

def create_sale_transaction(db: Session, sale_data: SaleCreate) -> Sale:
    """
    Coordinates the entire checkout transaction:
    1. Validates stock levels for all products in the cart.
    2. Dynamically calculates totals using database prices.
    3. Atomically deducts stock levels.
    4. Records the Sale receipt and nested items.
    """
    # 1. Generate a clean unique receipt number (e.g., REC-8A9F2C1B)
    receipt_number = f"REC-{str(uuid.uuid4()).upper()[:8]}"
    
    total_amount = 0.0
    sales_items_to_create = []

    # 2. Process each item in the inbound cart request
    for item in sale_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {item.product_id} does not exist."
            )
            
        if product.current_stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.name}. Available: {product.current_stock}, Requested: {item.quantity}"
            )
            
        # Freeze the actual shop price at the exact moment of sale
        current_unit_price = product.price
        total_amount += current_unit_price * item.quantity
        
        # Deduct stock directly from the database entity
        product.current_stock -= item.quantity
        
        # Build the sub-item row
        db_sales_item = SalesItem(
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=current_unit_price
        )
        sales_items_to_create.append(db_sales_item)

    # 3. Create the parent sale row
    db_sale = Sale(
        receipt_number=receipt_number,
        total_amount=total_amount,
        payment_method=sale_data.payment_method,
        timestamp=datetime.utcnow()
    )
    
    # Associate the items via relationship; SQLAlchemy handles the foreign keys automatically
    db_sale.sales_items = sales_items_to_create

    # 4. Save everything in a single atomic transaction block
    try:
        db.add(db_sale)
        db.commit()
        db.refresh(db_sale)
        return db_sale
    except Exception:
        db.rollback()  # Protect data integrity if anything breaks mid-loop
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the sales transaction."
        )


def get_all_sales(db: Session):
    """Fetches all past sale receipts for historical analysis."""
    return db.query(Sale).all()


def get_sale_by_id(db: Session, sale_id: int):
    """Fetches a specific sale receipt by its database identifier."""
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sale transaction with ID {sale_id} not found."
        )
    return sale