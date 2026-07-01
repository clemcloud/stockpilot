from typing import Optional
from pydantic import BaseModel , Field
from datetime import datetime

class ProductCreate(BaseModel):
    name : str = Field(..., min_length=1, max_length=100)
    sku : str = Field(..., min_length=1, max_length=50)
    description : Optional[str] = Field(None, max_length=200)
    price : float = Field(..., gt=0)
    current_stock : int = Field(..., ge=0)
    min_stock_level : int = Field(..., ge=0)

class InventoryLogCreate(BaseModel):
    product_id : int
    change_amount : int
    log_type : str = Field(..., pattern="^(addition|removal)$")
    notes : Optional[str] = Field(None, max_length=200)

class productUpdate(BaseModel):
    name : Optional[str] = Field(None, min_length=1, max_length=100)
    sku : Optional[str] = Field(None, min_length=1, max_length=50)
    description : Optional[str] = Field(None, max_length=200)
    price : Optional[float] = Field(None, gt=0)
    current_stock : Optional[int] = Field(None, ge=0)
    min_stock_level : Optional[int] = Field(None, ge=0)


class ProductResponse(BaseModel):
    id : int
    name : str
    sku : str
    description : Optional[str]
    price : float
    current_stock : int
    min_stock_level : int

    model_config = {"from_attributes": True}


class InventoryLogResponse(BaseModel):
    id : int
    product_id : int
    change_amount : int
    log_type : str
    notes : Optional[str]
    timestamp : datetime

    model_config = {"from_attributes": True}