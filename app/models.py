from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    """Tracks administrative and staff user authentication profiles."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="staff")  # admin, manager, staff
    is_active = Column(Boolean, default=True)


class Product(Base):
    """Stores product catalogs, pricing snapshots, and core tracking thresholds."""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    current_stock = Column(Integer, default=0)
    min_stock_level = Column(Integer, default=10)
    price = Column(Float, nullable=False)
    
    # Relationships
    inventory_logs = relationship("InventoryLog", back_populates="product")
    sale_items = relationship("SaleItem", back_populates="product")


class InventoryLog(Base):
    """Audit ledger tracking manual restocks, shrinkage adjustments, and stock levels."""
    __tablename__ = "inventory_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity_change = Column(Integer, nullable=False)  # e.g., +100 for restock, -5 for damage
    log_type = Column(String, nullable=False)          # RESTOCK, DAMAGE_ADJUSTMENT, AUDIT
    timestamp = Column(DateTime, default=datetime.utcnow)
    notes = Column(String, nullable=True)
    
    product = relationship("Product", back_populates="inventory_logs")


class Sale(Base):
    """Tracks direct Point of Sale checkout transactions across terminals."""
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    receipt_number = Column(String, unique=True, index=True, nullable=False)
    total_amount = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False)    # CASH, CARD, MOBILE
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    items = relationship("SaleItem", back_populates="sale")


class SaleItem(Base):
    """Bridge ledger tracking explicit line-item counts and prices per receipt."""
    __tablename__ = "sale_items"
    
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)         # Locked pricing snapshot
    
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")