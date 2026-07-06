from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse  # FIXED: Imported the missing class
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.database import Base, engine
import app.models
from app.api import auth, users, products, inventory, sales

# Initialize Database Entities
Base.metadata.create_all(bind=engine)

app = FastAPI(title="StockPilot", version="1.0.0")

# Security Cross-Origin Request Interceptor Pipeline
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Asset Mountings
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# Register Microservice API Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(inventory.router)
app.include_router(sales.router)


# ================= UI ROUTING CONSOLE VIEWS =================

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html"
    )


@app.get("/products-page", response_class=HTMLResponse)
def products_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="products.html"
    )


@app.get("/inventory-page", response_class=HTMLResponse)
def inventory_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="inventory.html"
    )


@app.get("/sales-page", response_class=HTMLResponse)
def sales_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="sales.html"
    )


@app.get("/terminal-page", response_class=HTMLResponse)
def terminal_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="terminal.html"
    )


@app.get("/signup-page", response_class=HTMLResponse)
def signup_page(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="signup.html"
    )

    
# ================= INFRASTRUCTURE UTILITY NODES =================

@app.get("/health")
def health():
    return {"status": "healthy", "app": "StockPilot"}