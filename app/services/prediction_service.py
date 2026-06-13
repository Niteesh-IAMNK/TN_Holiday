import datetime
from sqlalchemy.orm import Session
from loguru import logger
from app.database.models import Alert, District, HolidayPrediction
from app.services.message_formatter import MessageFormatter
from app.services.telegram_service import TelegramService

class PredictionService:
    """Predictive safety engine computing regional public closure likelihood variables."""

    def __init__(self):
        self.telegram = TelegramService()

    def execute_inference_matrix(self, db: Session):
        logger.info("Running deterministic regional holiday probability matrix...")
        districts = db.query(District).all()
        
        # Lookback frame targeting historical triggers inside the current day context window
        today_start = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        for district in districts:
            # Query matching metrics inside current geographical scopes
            recent_alerts = db.query(Alert).filter(
                Alert.district_id == district.id,
                Alert.created_at >= today_start
            ).all()

            # Process state profiles
            has_red_alert = any("red alert" in a.title.lower() or "red alert" in a.content.lower() for a in recent_alerts)
            has_orange_alert = any("orange alert" in a.title.lower() or "orange alert" in a.content.lower() for a in recent_alerts)
            has_heavy_rain = any("heavy rain" in a.title.lower() or "downpour" in a.content.lower() for a in recent_alerts)
            was_closed_today = any("holiday" in a.title.lower() or "closed" in a.content.lower() for a in recent_alerts)

            # Compute Probability Levels using Phase 5 Business Logic Rules
            probability_level = "LOW"
            reasoning = "Standard local weather trends observed. Operational risk remains minimal."

            if has_red_alert and has_heavy_rain and was_closed_today:
                probability_level = "HIGH"
                reasoning = "Severe meteorological vectors matching current localized disruptions warrant a high probability of extended institutional closure."
            elif has_orange_alert and has_heavy_rain:
                probability_level = "MEDIUM"
                reasoning = "Substantial precipitation and hazard alerts indicate possible administrative intervention."

            # Save prediction artifact
            prediction = HolidayPrediction(
                alert_id=recent_alerts[0].id if recent_alerts else 1,
                predicted_date=datetime.datetime.utcnow() + datetime.timedelta(days=1),
                confidence_score=95 if probability_level == "HIGH" else (60 if probability_level == "MEDIUM" else 15),
                is_holiday=(probability_level in ["HIGH", "MEDIUM"]),
                ai_reasoning=reasoning
            )
            db.add(prediction)
            db.commit()

            # Alert if Risk Index hits medium/high thresholds
            if probability_level in ["HIGH", "MEDIUM"]:
                msg = MessageFormatter.format_message(
                    category="TOMORROW_HOLIDAY_PROBABILITY",
                    district=district.name,
                    date_str=(datetime.datetime.utcnow() + datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
                    title=f"Risk Level: {probability_level} ({prediction.confidence_score}% Scale Variance)",
                    content=reasoning,
                    url="https://mausam.imd.gov.in/chennai/"
                )
                self.telegram.send_channel_message(msg)