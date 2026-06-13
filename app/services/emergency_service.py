from sqlalchemy.orm import Session
from loguru import logger
from app.scrapers.government_scraper import GovernmentScraper
from app.services.dedup_service import DedupService
from app.services.message_formatter import MessageFormatter
from app.services.telegram_service import TelegramService
from app.database.models import Alert, District, Source, PriorityEnum

class EmergencyService:
    def __init__(self):
        self.scraper = GovernmentScraper()
        self.telegram = TelegramService()

    def process_orders(self, db: Session):
        logger.info("Checking state control channels for emergency safety directives...")
        source = db.query(Source).filter(Source.name == "Emergency Bulletins").first()
        if not source:
            source = Source(name="Emergency Bulletins", url="https://www.tn.gov.in")
            db.add(source)
            db.commit()

        alerts = self.scraper.press_releases("https://www.tn.gov.in/pressrelease")
        for alert in alerts:
            if alert["category"] != "EMERGENCY_ALERT":
                continue

            district = db.query(District).filter(District.name == alert["district"]).first()
            district_id = district.id if district else None

            if DedupService.is_duplicate(db, "EMERGENCY_ALERT", district_id, alert["district"], "immediate", alert["title"]):
                continue

            new_alert = Alert(
                title=alert["title"], content=alert["content"], source_id=source.id,
                district_id=district_id, priority=PriorityEnum.CRITICAL, raw_url=alert["url"],
                published_at=__import__('datetime').datetime.utcnow()
            )
            db.add(new_alert)
            db.commit()

            msg = MessageFormatter.format_message("EMERGENCY_ALERT", alert["district"], "Immediate Threat Context", alert["title"], alert["content"], alert["url"])
            self.telegram.send_channel_message(msg)