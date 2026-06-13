from loguru import logger
from app.database.session import SessionLocal
from app.services.transport_service import TransportService

def run_transport_job():
    db = SessionLocal()
    try:
        TransportService().process_disruptions(db)
    except Exception as e:
        logger.error(f"Error handling commercial transport metrics: {e}")
    finally:
        db.close()