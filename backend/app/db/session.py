from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from tenacity import retry, stop_after_attempt, wait_fixed
from app.core.config import DATABASE_URL

class Base(DeclarativeBase):
    pass

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

@retry(stop=stop_after_attempt(20), wait=wait_fixed(1))
def ping_db() -> None:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
