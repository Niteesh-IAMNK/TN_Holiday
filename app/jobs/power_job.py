from loguru import logger
from app.database.session import SessionLocal
from app.services.power_service import PowerService

def run_power_job():
    db = SessionLocal()
    try:
        PowerService().process_outages(db)
    except Exception as e:
        logger.error(f"Error updating structural utility grid states: {e}")
    finally:
        db.close()