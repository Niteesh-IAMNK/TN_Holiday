from loguru import logger
from app.database.session import SessionLocal
from app.services.cyclone_service import CycloneService
from app.database.models import SchedulerRun, RunStatusEnum
from datetime import datetime

def run_cyclone_job():
    logger.info("[JOB START] Coastal Cyclone tracking sequence initiated.")
    db = SessionLocal()
    run_metric = SchedulerRun(job_name="cyclone_job", status=RunStatusEnum.RUNNING)
    db.add(run_metric)
    db.commit()

    try:
        service = CycloneService()
        service.process_cyclone_alerts(db)
        
        run_metric.status = RunStatusEnum.SUCCESS
        run_metric.logs_summary = "Cyclone matrix check completed successfully."
    except Exception as e:
        logger.error(f"[JOB FAILED] Exception thrown in cyclone processing task: {e}")
        run_metric.status = RunStatusEnum.FAILED
        run_metric.logs_summary = f"Failure Exception: {str(e)}"
    finally:
        run_metric.finished_at = datetime.utcnow()
        db.commit()
        db.close()
        logger.info("[JOB END] Coastal Cyclone tracking sequence completed.")