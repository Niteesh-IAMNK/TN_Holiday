from sqlalchemy.orm import Session
from loguru import logger
from app.scrapers.news_scraper import NewsScraper
from app.services.dedup_service import DedupService
from app.services.message_formatter import MessageFormatter
from app.services.telegram_service import TelegramService
from app.database.models import Alert, District, Source, PriorityEnum

class PowerService:
    def __init__(self):
        self.scraper = NewsScraper()
        self.telegram = TelegramService()

    def process_outages(self, db: Session):
        logger.info("Processing TANGEDCO power grid maintenance notifications...")
        source = db.query(Source).filter(Source.name == "TANGEDCO Data").first()
        if not source:
            source = Source(name="TANGEDCO Data", url="https://news.google.com")
            db.add(source)
            db.commit()

        rss_url = "https://news.google.com/rss/search?q=(TANGEDCO+OR+substation)+power+shutdown+maintenance&hl=en-IN&gl=IN"
        alerts = self.scraper.scrape_media_source(rss_url)
        for alert in alerts:
            if "power" not in alert["title"].lower() and "shutdown" not in alert["title"].lower():
                continue

            district = db.query(District).filter(District.name == alert["district"]).first()
            district_id = district.id if district else None

            if DedupService.is_duplicate(db, "POWER_ALERT", district_id, alert["district"], "scheduled", alert["title"]):
                continue

            new_alert = Alert(
                title=alert["title"], content=alert["content"], source_id=source.id,
                district_id=district_id, priority=PriorityEnum.LOW, raw_url=alert["url"],
                published_at=__import__('datetime').datetime.utcnow()
            )
            db.add(new_alert)
            db.commit()

            msg = MessageFormatter.format_message("POWER_ALERT", alert["district"], "Scheduled Outage Matrix", alert["title"], alert["content"], alert["url"])
            self.telegram.send_channel_message(msg)