from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.inventory import InventoryLogCreate, InventoryLogResponse
from app.services.inventory_service import create_inventory_log
from app.services.threshold import get_low_stock_alerts

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.post("/log", response_model=InventoryLogResponse, status_code=201)
def log_inventory(data: InventoryLogCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return create_inventory_log(db, data)


@router.get("/alerts")
def stock_alerts(db: Session = Depends(get_db), _=Depends(get_current_user)):
    low_stock = get_low_stock_alerts(db)
    return {
        "total_alerts": len(low_stock),
        "products": [{"id": p.id, "name": p.name, "sku": p.sku, "current_stock": p.current_stock, "min_stock_level": p.min_stock_level} for p in low_stock]
    }