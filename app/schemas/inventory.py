# The schemas/sales.py file defines the data models for request and response validation.
# Aligned perfectly with the Sales and SaleItems relational database tables.
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# ==========================================
#               SALE ITEM SCHEMAS
# ==========================================

class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int


class SaleItemUpdate(BaseModel):
    product_id: Optional[int] = None
    quantity: Optional[int] = None


class SaleItemResponse(BaseModel):
    id: int
    sale_id: int
    product_id: int
    quantity: int
    unit_price: float  # Captured snapshot of the price at checkout

    class Config:
        from_attributes = True


# ==========================================
#                 SALE SCHEMAS
# ==========================================

class SaleCreate(BaseModel):
    payment_method: str  # CASH, CARD, or MOBILE
    items: List[SaleItemCreate]  # The incoming checkout shopping basket


class SaleUpdate(BaseModel):
    payment_method: Optional[str] = None


class SaleResponse(BaseModel):
    id: int
    receipt_number: str
    total_amount: float
    payment_method: str
    timestamp: datetime
    items: List[SaleItemResponse]  # Nested list showing exactly what items were bought

    class Config:
        from_attributes = True