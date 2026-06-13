from sqlalchemy.orm import Session
from loguru import logger
from app.scrapers.news_scraper import NewsScraper
from app.services.dedup_service import DedupService
from app.services.message_formatter import MessageFormatter
from app.services.telegram_service import TelegramService
from app.database.models import Alert, District, Source, PriorityEnum

class FloodService:
    """Monitors localized urban flooding, river overflows, and waterlogging indicators."""

    def __init__(self):
        self.news_scraper = NewsScraper()
        self.telegram_service = TelegramService()

    def process_flood_alerts(self, db: Session):
        logger.info("Executing Flood and Waterlogging monitoring loop...")
        
        source = db.query(Source).filter(Source.name == "Flood Tracking RSS").first()
        if not source:
            source = Source(name="Flood Tracking RSS", url="https://news.google.com/rss/search?q=Tamil+Nadu+floods+waterlogging")
            db.add(source)
            db.commit()

        rss_target = "https://news.google.com/rss/search?q=Tamil+Nadu+flooding+waterlogging+inundation&hl=en-IN&gl=IN"
        alerts = self.news_scraper.scrape_media_source(rss_target)

        for alert in alerts:
            if "flood" not in alert["title"].lower() and "waterlogging" not in alert["title"].lower():
                continue

            district = db.query(District).filter(District.name == alert["district"]).first()
            district_id = district.id if district else None

            if DedupService.is_duplicate(db, "FLOOD_ALERT", district_id, alert["district"], "active", alert["title"]):
                continue

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

            formatted_msg = MessageFormatter.format_message(
                category="FLOOD_ALERT",
                district=alert["district"],
                date_str="Active Inundation Notice",
                title=alert["title"],
                content=alert["content"],
                url=alert["url"]
            )
            self.telegram_service.send_channel_message(formatted_msg)