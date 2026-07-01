from sqlalchemy.orm import Session
from app.models import Product

def get_low_stock_alerts(db: Session):
    """
    Scans the database and returns a list of all products 
    whose current stock has dropped to or below their safety threshold.
    """
    return db.query(Product).filter(Product.current_stock <= Product.min_stock_level).all()