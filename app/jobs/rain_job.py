from loguru import logger
from app.database.session import SessionLocal
from app.services.rain_service import RainService
from app.database.models import SchedulerRun, RunStatusEnum
from datetime import datetime

def run_rain_holiday_job():
    logger.info("[JOB START] Rain Holiday verification sequence initiated.")
    db = SessionLocal()
    run_metric = SchedulerRun(job_name="rain_holiday_job", status=RunStatusEnum.RUNNING)
    db.add(run_metric)
    db.commit()

    try:
        service = RainService()
        service.process_rain_holidays(db)
        
        run_metric.status = RunStatusEnum.SUCCESS
        run_metric.logs_summary = "Rain holiday validation routine finished cleanly."
    except Exception as e:
        logger.error(f"[JOB FAILED] Exception thrown in rain holiday tracking task: {e}")
        run_metric.status = RunStatusEnum.FAILED
        run_metric.logs_summary = f"Failure Exception: {str(e)}"
    finally:
        run_metric.finished_at = datetime.utcnow()
        db.commit()
        db.close()
        logger.info("[JOB END] Rain Holiday verification sequence completed.")