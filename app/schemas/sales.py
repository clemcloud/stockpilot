from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int


class SaleCreate(BaseModel):
    payment_method: str
    items: List[SaleItemCreate]
    owner_id: int


class SaleItemResponse(BaseModel):
    id: int
    sale_id: int
    product_id: int
    quantity: int
    unit_price: float

    model_config = {"from_attributes": True}


class SaleResponse(BaseModel):
    id: int
    receipt_number: str
    total_amount: float
    payment_method: str
    timestamp: datetime
    sales_items: List[SaleItemResponse]

    model_config = {"from_attributes": True}