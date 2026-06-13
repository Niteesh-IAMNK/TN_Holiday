from sqlalchemy.orm import Session
from loguru import logger
from app.scrapers.government_scraper import GovernmentScraper
from app.services.dedup_service import DedupService
from app.services.message_formatter import MessageFormatter
from app.services.telegram_service import TelegramService
from app.database.models import Alert, District, Source, PriorityEnum

class WeatherService:
    """Processes IMD weather bulletins and regional weather warnings."""

    def __init__(self):
        self.gov_scraper = GovernmentScraper()
        self.telegram_service = TelegramService()

    def process_weather_alerts(self, db: Session):
        logger.info("Executing Weather Bulletin processing loop...")
        
        source = db.query(Source).filter(Source.name == "IMD Bulletins").first()
        if not source:
            source = Source(name="IMD Bulletins", url="https://mausam.imd.gov.in/chennai/")
            db.add(source)
            db.commit()

        # Real-world fallback press releases targeting regional climate adjustments
        target_url = "https://www.tn.gov.in/pressrelease"
        alerts = self.gov_scraper.scrape_press_releases(target_url)

        for alert in alerts:
            if alert["category"] not in ["WEATHER_ALERT", "EMERGENCY_ALERT"]:
                continue

            district = db.query(District).filter(District.name == alert["district"]).first()
            district_id = district.id if district else None

            if DedupService.is_duplicate(db, "WEATHER_ALERT", district_id, alert["district"], "current", alert["title"]):
                continue

            new_alert = Alert(
                title=alert["title"],
                content=alert["content"],
                source_id=source.id,
                district_id=district_id,
                priority=PriorityEnum.MEDIUM,
                raw_url=alert["url"],
                published_at=alert.get("published_raw", type('datetime', (), {'utcnow': staticmethod(lambda: __import__('datetime').datetime.utcnow())})().utcnow())
            )
            db.add(new_alert)
            db.commit()

            formatted_msg = MessageFormatter.format_message(
                category="WEATHER_ALERT",
                district=alert["district"],
                date_str="Current Bulletin",
                title=alert["title"],
                content=alert["content"],
                url=alert["url"]
            )
            self.telegram_service.send_channel_message(formatted_msg)