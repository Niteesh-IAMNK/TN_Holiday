from loguru import logger
from app.database.session import SessionLocal
from app.services.flood_service import FloodService
from app.database.models import SchedulerRun, RunStatusEnum
from datetime import datetime

def run_flood_job():
    logger.info("[JOB START] Urban Inundation and Flood sequence initiated.")
    db = SessionLocal()
    run_metric = SchedulerRun(job_name="flood_job", status=RunStatusEnum.RUNNING)
    db.add(run_metric)
    db.commit()

    try:
        service = FloodService()
        service.process_flood_alerts(db)
        
        run_metric.status = RunStatusEnum.SUCCESS
        run_metric.logs_summary = "Inundation alerts tracked smoothly."
    except Exception as e:
        logger.error(f"[JOB FAILED] Exception thrown in flood monitoring task: {e}")
        run_metric.status = RunStatusEnum.FAILED
        run_metric.logs_summary = f"Failure Exception: {str(e)}"
    finally:
        run_metric.finished_at = datetime.utcnow()
        db.commit()
        db.close()
        logger.info("[JOB END] Urban Inundation and Flood sequence completed.")