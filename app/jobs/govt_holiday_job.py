from loguru import logger
from app.database.session import SessionLocal
from app.services.govt_holiday_service import GovtHolidayService

def run_govt_holiday_job():
    db = SessionLocal()
    try:
        GovtHolidayService().process_holidays(db)
    except Exception as e:
        logger.error(f"Error executing public holiday synchronization task: {e}")
    finally:
        db.close()