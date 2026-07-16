from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import Sale, SalesItem, Product
from app.schemas.sales import SaleCreate
from app.services.threshold import check_and_notify
from datetime import datetime
import uuid


def create_sale_transaction(db: Session, sale_data: SaleCreate, user_id: int) -> Sale:
    receipt_number = f"REC-{str(uuid.uuid4()).upper()[:8]}"
    total_amount = 0.0

    # 1. Create the parent Sale object immediately tied to the dynamic incoming user_id
    db_sale = Sale(
        receipt_number=receipt_number,
        total_amount=0.0,  
        payment_method=sale_data.payment_method,
        timestamp=datetime.utcnow(),
        owner_id=user_id  # 👈 Tied strictly to the store owner passing it from the frontend
    )
    
    try:
        db.add(db_sale)
        db.flush()  # Generates db_sale.id safely within the transaction block

        for item in sale_data.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()

            if not product:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with ID {item.product_id} does not exist."
                )

            if product.current_stock < item.quantity:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for {product.name}. Available: {product.current_stock}, Requested: {item.quantity}"
                )

            current_unit_price = product.price
            total_amount += current_unit_price * item.quantity
            product.current_stock -= item.quantity

            # Trigger stock alert notifications safely
            check_and_notify(db=db, product=product)

            # 2. Bind the child SalesItem directly to the parent sale_id
            db_sales_item = SalesItem(
                sale_id=db_sale.id,  
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=current_unit_price
            )
            db.add(db_sales_item)  

        # 3. Update the final total calculated amount
        db_sale.total_amount = total_amount
        
        # 4. Commit the atomic unit to RDS
        db.commit()
        db.refresh(db_sale)
        return db_sale

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the sales transaction."
        )


def get_all_sales(db: Session, user_id: int):
    # ✅ FIXED: Strict multi-tenant data isolation. No shared fallback leak.
    return db.query(Sale).filter(Sale.owner_id == user_id).all()


def get_sale_by_id(db: Session, sale_id: int, user_id: int):
    # ✅ FIXED: Completely isolated view boundaries.
    sale = db.query(Sale).filter(
        Sale.id == sale_id,
        Sale.owner_id == user_id
    ).first()
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sale transaction with ID {sale_id} not found or access denied."
        )
    return sale