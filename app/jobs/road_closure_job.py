from loguru import logger
from app.database.session import SessionLocal
from app.services.road_closure_service import RoadClosureService

def run_road_closure_job():
    db = SessionLocal()
    try:
        RoadClosureService().process_closures(db)
    except Exception as e:
        logger.error(f"Error logging structural traffic network variations: {e}")
    finally:
        db.close()