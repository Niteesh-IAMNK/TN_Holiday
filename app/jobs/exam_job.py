from loguru import logger
from app.database.session import SessionLocal
from app.services.exam_service import ExamService

def run_exam_job():
    db = SessionLocal()
    try:
        ExamService().process_notifications(db)
    except Exception as e:
        logger.error(f"Error monitoring exam schedule tracking indexes: {e}")
    finally:
        db.close()