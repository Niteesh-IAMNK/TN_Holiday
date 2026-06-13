from sqlalchemy.orm import Session
from loguru import logger
from app.scrapers.news_scraper import NewsScraper
from app.services.dedup_service import DedupService
from app.services.message_formatter import MessageFormatter
from app.services.telegram_service import TelegramService
from app.database.models import Alert, District, Source, PriorityEnum

class CycloneService:
    """Monitors critical cyclonic movements or depressions in the Bay of Bengal affecting TN coastal zones."""

    def __init__(self):
        self.news_scraper = NewsScraper()
        self.telegram_service = TelegramService()

    def process_cyclone_alerts(self, db: Session):
        logger.info("Executing Cyclone tracking loop...")
        
        source = db.query(Source).filter(Source.name == "Cyclone Warning Feed").first()
        if not source:
            source = Source(name="Cyclone Warning Feed", url="https://news.google.com/rss/search?q=Cyclone+Tamil+Nadu")
            db.add(source)
            db.commit()

        rss_target = "https://news.google.com/rss/search?q=Cyclone+Depression+Tamil+Nadu+Coast&hl=en-IN&gl=IN"
        alerts = self.news_scraper.scrape_media_source(rss_target)

        for alert in alerts:
            if "cyclone" not in alert["title"].lower() and "depression" not in alert["title"].lower():
                continue

            district = db.query(District).filter(District.name == alert["district"]).first()
            district_id = district.id if district else None

            if DedupService.is_duplicate(db, "CYCLONE_ALERT", district_id, alert["district"], "immediate", alert["title"]):
                continue

            new_alert = Alert(
                title=alert["title"],
                content=alert["content"],
                source_id=source.id,
                district_id=district_id,
                priority=PriorityEnum.CRITICAL,
                raw_url=alert["url"],
                published_at=alert.get("published_raw", type('datetime', (), {'utcnow': staticmethod(lambda: __import__('datetime').datetime.utcnow())})().utcnow())
            )
            db.add(new_alert)
            db.commit()

            formatted_msg = MessageFormatter.format_message(
                category="CYCLONE_ALERT",
                district=alert["district"],
                date_str="Immediate Safety Warning",
                title=alert["title"],
                content=alert["content"],
                url=alert["url"]
            )
            self.telegram_service.send_channel_message(formatted_msg)