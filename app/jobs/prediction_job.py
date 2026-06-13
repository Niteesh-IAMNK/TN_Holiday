from loguru import logger
from app.database.session import SessionLocal
from app.services.prediction_service import PredictionService

def run_prediction_job():
    logger.info("[ANALYSIS ENGINE] Launching analytical prediction execution sequence...")
    db = SessionLocal()
    try:
        PredictionService().execute_inference_matrix(db)
    except Exception as e:
        logger.error(f"Error running predictive calculation runs: {e}")
    finally:
        db.close()