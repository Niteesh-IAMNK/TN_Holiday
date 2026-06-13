from sqlalchemy.orm import Session
from loguru import logger
from app.scrapers.news_scraper import NewsScraper
from app.services.dedup_service import DedupService
from app.services.message_formatter import MessageFormatter
from app.services.telegram_service import TelegramService
from app.database.models import Alert, District, Source, PriorityEnum

class ExamService:
    def __init__(self):
        self.scraper = NewsScraper()
        self.telegram = TelegramService()

    def process_notifications(self, db: Session):
        logger.info("Evaluating educational circulars and university schedule alterations...")
        source = db.query(Source).filter(Source.name == "Academic Notifications").first()
        if not source:
            source = Source(name="Academic Notifications", url="https://news.google.com")
            db.add(source)
            db.commit()

        rss_url = "https://news.google.com/rss/search?q=(Anna+University+OR+DGE+OR+postponed)+exam+postponement+circular&hl=en-IN&gl=IN"
        alerts = self.scraper.scrape_media_source(rss_url)
        for alert in alerts:
            if alert["category"] != "EXAM_NOTIFICATION":
                continue

            district = db.query(District).filter(District.name == alert["district"]).first()
            district_id = district.id if district else None

            if DedupService.is_duplicate(db, "EXAM_NOTIFICATION", district_id, alert["district"], "academic", alert["title"]):
                continue

            new_alert = Alert(
                title=alert["title"], content=alert["content"], source_id=source.id,
                district_id=district_id, priority=PriorityEnum.MEDIUM, raw_url=alert["url"],
                published_at=__import__('datetime').datetime.utcnow()
            )
            db.add(new_alert)
            db.commit()

            msg = MessageFormatter.format_message("EXAM_NOTIFICATION", alert["district"], "Academic Changes", alert["title"], alert["content"], alert["url"])
            self.telegram.send_channel_message(msg)