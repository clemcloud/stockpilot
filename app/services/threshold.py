from sqlalchemy.orm import Session
from app.models import Product
from app.services.notification import publish_stock_event


def get_low_stock_alerts(db: Session, user_id: int = None):
    query = db.query(Product).filter(
        Product.current_stock <= Product.min_stock_level
    )
    if user_id:
        query = query.filter(Product.owner_id == user_id)
    return query.all()


def check_and_notify(db: Session, product: Product) -> bool:
    if product.current_stock <= product.min_stock_level:
        publish_stock_event(
            product_id=product.id,
            product_name=product.name,
            sku=product.sku,
            current_stock=product.current_stock,
            min_stock_level=product.min_stock_level,
        )
        return True
    return False