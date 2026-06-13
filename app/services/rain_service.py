from sqlalchemy.orm import Session
from loguru import logger
from app.scrapers.news_scraper import NewsScraper
from app.services.dedup_service import DedupService
from app.services.message_formatter import MessageFormatter
from app.services.telegram_service import TelegramService
from app.database.models import Alert, District, Source, PriorityEnum

class RainService:
    """Monitors school/college rain holidays using media streams and collector feeds."""

    def __init__(self):
        self.news_scraper = NewsScraper()
        self.telegram_service = TelegramService()

    def process_rain_holidays(self, db: Session):
        logger.info("Executing Rain Holiday processing loop...")
        
        # Pull active source object or seed default
        source = db.query(Source).filter(Source.name == "Google News RSS").first()
        if not source:
            source = Source(name="Google News RSS", url="https://news.google.com/rss/search?q=Tamil+Nadu+school+college+holiday")
            db.add(source)
            db.commit()

        # Target regional rain query filter
        rss_target = "https://news.google.com/rss/search?q=Tamil+Nadu+school+college+holiday+heavy+rain&hl=en-IN&gl=IN"
        alerts = self.news_scraper.scrape_media_source(rss_target)

        for alert in alerts:
            if alert["category"] != "RAIN_HOLIDAY":
                continue

            # Fetch matching district identity mapping
            district = db.query(District).filter(District.name == alert["district"]).first()
            district_id = district.id if district else None

            # Deduplicate
            if DedupService.is_duplicate(db, "RAIN_HOLIDAY", district_id, alert["district"], "tomorrow", alert["title"]):
                continue

            # Save Alert to DB
            new_alert = Alert(
                title=alert["title"],
                content=alert["content"],
                source_id=source.id,
                district_id=district_id,
                priority=PriorityEnum.HIGH,
                raw_url=alert["url"],
                published_at=alert.get("published_raw", type('datetime', (), {'utcnow': staticmethod(lambda: __import__('datetime').datetime.utcnow())})().utcnow())
            )
            db.add(new_alert)
            db.commit()

            # Disseminate to Telegram Channel
            formatted_msg = MessageFormatter.format_message(
                category="RAIN_HOLIDAY",
                district=alert["district"],
                date_str="Tomorrow",
                title=alert["title"],
                content=alert["content"],
                url=alert["url"]
            )
            self.telegram_service.send_channel_message(formatted_msg)