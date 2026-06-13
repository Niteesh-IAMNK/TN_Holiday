import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from loguru import logger
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from app.config import settings
from app.database.session import engine, Base

# Job Module Links
from app.jobs.rain_job import run_rain_holiday_job
from app.jobs.weather_job import run_weather_job
from app.jobs.cyclone_job import run_cyclone_job
from app.jobs.flood_job import run_flood_job
from app.jobs.dam_job import run_dam_job
from app.jobs.govt_holiday_job import run_govt_holiday_job
from app.jobs.road_closure_job import run_road_closure_job
from app.jobs.transport_job import run_transport_job
from app.jobs.power_job import run_power_job
from app.jobs.emergency_job import run_emergency_job
from app.jobs.exam_job import run_exam_job
from app.jobs.prediction_job import run_prediction_job

class HealthCheckHandler(BaseHTTPRequestHandler):
    """Native, zero-dependency HTTP endpoint for orchestration engine context evaluation."""
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "healthy", "engine": "operational", "scheduler": "active"}')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return # Override default stdout logs to keep production logs clean

def start_health_server():
    server = HTTPServer(('0.0.0.0', 8000), HealthCheckHandler)
    logger.info("Internal health telemetry listener online at port: 8000")
    server.serve_forever()

def init_db():
    Base.metadata.create_all(bind=engine)

def main():
    logger.info("Booting TN Automation Framework Phase 5 Operational System...")
    init_db()

    # Launch Health Node Thread asynchronously
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()

    scheduler = BlockingScheduler(timezone="Asia/Kolkata")

    # Linked Base Phases 1-4 Tasks
    scheduler.add_job(run_rain_holiday_job, trigger=CronTrigger(hour="5-23", minute="*/2"), id="cron_rain")
    scheduler.add_job(run_weather_job, trigger='interval', minutes=15, id="cron_weather")
    scheduler.add_job(run_cyclone_job, trigger='interval', minutes=15, id="cron_cyclone")
    scheduler.add_job(run_flood_job, trigger='interval', minutes=10, id="cron_flood")
    scheduler.add_job(run_dam_job, trigger='interval', minutes=15, id="cron_dam")

    # Phase 5 Processing Additions
    scheduler.add_job(run_govt_holiday_job, trigger='interval', hours=4, id="cron_govt_holiday")
    scheduler.add_job(run_road_closure_job, trigger='interval', minutes=10, id="cron_road")
    scheduler.add_job(run_transport_job, trigger='interval', minutes=15, id="cron_transport")
    scheduler.add_job(run_power_job, trigger='interval', hours=1, id="cron_power")
    scheduler.add_job(run_emergency_job, trigger='interval', minutes=5, id="cron_emergency")
    scheduler.add_job(run_exam_job, trigger='interval', hours=2, id="cron_exam")

    # Predictive Matrix Iteration Shifts: 5:30 PM, 7:00 PM, 9:00 PM, 5:30 AM IST
    prediction_hours = ["5", "17", "19", "21"]
    prediction_minutes = ["30", "0", "0", "30"]
    
    for hr, mn in zip(prediction_hours, prediction_minutes):
        scheduler.add_job(
            run_prediction_job,
            trigger=CronTrigger(hour=hr, minute=mn),
            id=f"probability_matrix_shift_{hr}_{mn}",
            max_instances=1,
            replace_existing=True
        )

    logger.success("All analytical workflows mounted successfully into APScheduler loops.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.warning("Graceful termination intercept verified. Closing engine threads...")

if __name__ == "__main__":
    main()