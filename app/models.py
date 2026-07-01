from app.database import Base
from sqlalchemy import Column, Integer, String , Float , DateTime , ForeignKey , Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    role = Column(String, default="user" )
    hashed_password = Column(String , nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    sku = Column(String, unique=True, index=True)
    current_stock = Column(Integer)
    min_stock_level = Column(Integer)

    inventory_logs = relationship("InventoryLog", back_populates="product" , cascade="all, delete-orphan")
    sales_item = relationship("SalesItem", back_populates="product" )



class InventoryLog(Base):
    __tablename__ = "inventory_logs"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    change_amount = Column(Integer)
    log_type = Column(String, nullable=False)  # "addition" or "removal"
    notes = Column(String , nuillable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="inventory_logs")


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    receipt_number = Column(String, unique=True, index=True)
    total_amount = Column(Float)
    payment_method = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    sales_items = relationship("SalesItem", back_populates="sale" , cascade="all, delete-orphan")

class SalesItem(Base):
    __tablename__ = "sales_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    unit_price = Column(Float)

    sale = relationship("Sale", back_populates="sales_items")
    product = relationship("Product", back_populates="sales_item")

