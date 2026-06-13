from loguru import logger
from app.database.session import SessionLocal
from app.services.weather_service import WeatherService
from app.database.models import SchedulerRun, RunStatusEnum
from datetime import datetime

def run_weather_job():
    logger.info("[JOB START] IMD Weather verification sequence initiated.")
    db = SessionLocal()
    run_metric = SchedulerRun(job_name="weather_job", status=RunStatusEnum.RUNNING)
    db.add(run_metric)
    db.commit()

    try:
        service = WeatherService()
        service.process_weather_alerts(db)
        
        run_metric.status = RunStatusEnum.SUCCESS
        run_metric.logs_summary = "Weather metrics processing executed smoothly."
    except Exception as e:
        logger.error(f"[JOB FAILED] Exception thrown in weather task: {e}")
        run_metric.status = RunStatusEnum.FAILED
        run_metric.logs_summary = f"Failure Exception: {str(e)}"
    finally:
        run_metric.finished_at = datetime.utcnow()
        db.commit()
        db.close()
        logger.info("[JOB END] IMD Weather verification sequence completed.")