import sys
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# Configure Loguru output patterns
logger.remove()
logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>", level=settings.LOG_LEVEL)
logger.add(settings.LOG_FILE, rotation="10 MB", retention="30 days", level=settings.LOG_LEVEL, compression="zip")

try:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    logger.critical(f"Failed to create database engine database URL structure. Error: {e}")
    raise e

Base = declarative_base()

def get_db():
    """Context manager style database session handling."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()