from loguru import logger
from app.database.session import SessionLocal
from app.services.emergency_service import EmergencyService

def run_emergency_job():
    db = SessionLocal()
    try:
        EmergencyService().process_orders(db)
    except Exception as e:
        logger.error(f"Error parsing emergency state control vectors: {e}")
    finally:
        db.close()