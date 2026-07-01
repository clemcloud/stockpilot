from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session , DeclarativeBase
from app.config import settings

class Base(DeclarativeBase):
    pass

engine = create_engine(settings.DATABASE_URL)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = session_local()
    try:
        yield db
    finally:
        db.close()