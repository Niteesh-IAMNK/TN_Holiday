from loguru import logger
from app.database.session import SessionLocal
from app.services.dam_service import DamService
from app.database.models import SchedulerRun, RunStatusEnum
from datetime import datetime

def run_dam_job():
    logger.info("[JOB START] Reservoir metrics collection sequence initiated.")
    db = SessionLocal()
    run_metric = SchedulerRun(job_name="dam_job", status=RunStatusEnum.RUNNING)
    db.add(run_metric)
    db.commit()

    try:
        service = DamService()
        service.process_dam_alerts(db)
        
        run_metric.status = RunStatusEnum.SUCCESS
        run_metric.logs_summary = "Dam discharge verification routine completed."
    except Exception as e:
        logger.error(f"[JOB FAILED] Exception thrown in dam reporting task: {e}")
        run_metric.status = RunStatusEnum.FAILED
        run_metric.logs_summary = f"Failure Exception: {str(e)}"
    finally:
        run_metric.finished_at = datetime.utcnow()
        db.commit()
        db.close()
        logger.info("[JOB END] Reservoir metrics collection sequence completed.")