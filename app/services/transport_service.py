from sqlalchemy.orm import Session
from loguru import logger
from app.scrapers.news_scraper import NewsScraper
from app.services.dedup_service import DedupService
from app.services.message_formatter import MessageFormatter
from app.services.telegram_service import TelegramService
from app.database.models import Alert, District, Source, PriorityEnum

class TransportService:
    def __init__(self):
        self.scraper = NewsScraper()
        self.telegram = TelegramService()

    def process_disruptions(self, db: Session):
        logger.info("Analyzing transport infrastructure feeds...")
        source = db.query(Source).filter(Source.name == "Transit Alerts").first()
        if not source:
            source = Source(name="Transit Alerts", url="https://news.google.com")
            db.add(source)
            db.commit()

        rss_url = "https://news.google.com/rss/search?q=(TNSTC+OR+MTC+OR+Southern+Railway)+cancelled+suspended+delay&hl=en-IN&gl=IN"
        alerts = self.scraper.scrape_media_source(rss_url)
        for alert in alerts:
            if "train" not in alert["title"].lower() and "bus" not in alert["title"].lower() and "railway" not in alert["title"].lower():
                continue

            district = db.query(District).filter(District.name == alert["district"]).first()
            district_id = district.id if district else None

            if DedupService.is_duplicate(db, "TRANSPORT_ALERT", district_id, alert["district"], "today", alert["title"]):
                continue

            new_alert = Alert(
                title=alert["title"], content=alert["content"], source_id=source.id,
                district_id=district_id, priority=PriorityEnum.MEDIUM, raw_url=alert["url"],
                published_at=__import__('datetime').datetime.utcnow()
            )
            db.add(new_alert)
            db.commit()

            msg = MessageFormatter.format_message("TRANSPORT_ALERT", alert["district"], "Operational Window", alert["title"], alert["content"], alert["url"])
            self.telegram.send_channel_message(msg)