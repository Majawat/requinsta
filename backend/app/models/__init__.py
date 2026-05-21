from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

from app.models.user import User
from app.models.request import Request
from app.models.setting import Setting


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
