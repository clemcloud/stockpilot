from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
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

# Initialize Jinja2 templates pointing directly to your new folder
templates = Jinja2Templates(directory="frontend/templates")

# --- CORE API ROUTERS ---
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(inventory.router)
app.include_router(sales.router)


# --- UI WEB PAGES ---
@app.get("/login", response_class=HTMLResponse)
def get_login_page(request: Request):
    """Serves the premium glassmorphic login interface view."""
    return templates.TemplateResponse(request=request, name="login.html")
@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard_page(request: Request):
    """Serves the main enterprise dashboard control center view."""
    return templates.TemplateResponse(request=request, name="dashboard.html")


# --- SYSTEM MONITORING ---
@app.get("/health")
def health():
    return {"status": "healthy", "app": "StockPilot"}