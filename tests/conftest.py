import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from main import app

# 1. Setup the in-memory/file test database
engine = create_engine(
    "sqlite:///./test.db",
    connect_args={"check_same_thread": False}
)
TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# 2. Database reset fixture (runs automatically before each test)
@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# 3. THE MISSING PIECE: Explicitly define and export the client fixture!
@pytest.fixture
def client():
    return TestClient(app)

# 4. The authenticated headers fixture
@pytest.fixture
def auth_headers(client):
    # Registering the user
    client.post("/users", json={
        "username": "manager",
        "email": "manager@stockpilot.com",
        "password": "password123"
    })
    
    # Login form submission (using data= for OAuth2 compatibility)
    response = client.post("/auth/login", data={
        "username": "manager",
        "password": "password123"
    })
    
    if response.status_code != 200:
        raise RuntimeError(f"Fixture login failed: {response.text}")
        
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}