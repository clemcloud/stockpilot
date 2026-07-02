from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
import app.models
from app.api import auth, users, products, inventory, sales

Base.metadata.create_all(bind=engine)

app = FastAPI(title="StockPilot", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(inventory.router)
app.include_router(sales.router)


@app.get("/health")
def health():
    return {"status": "healthy", "app": "StockPilot"}