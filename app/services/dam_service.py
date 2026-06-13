from sqlalchemy.orm import Session
from loguru import logger
from app.scrapers.news_scraper import NewsScraper
from app.services.dedup_service import DedupService
from app.services.message_formatter import MessageFormatter
from app.services.telegram_service import TelegramService
from app.database.models import Alert, District, Source, PriorityEnum

class DamService:
    """Tracks inflow surges and surplus water discharge across 6 critical reservoirs."""

    DAMS = ["Chembarambakkam", "Mettur", "Vaigai", "Bhavanisagar", "Sathanur", "Papanasam"]

    def __init__(self):
        self.news_scraper = NewsScraper()
        self.telegram_service = TelegramService()

    def process_dam_alerts(self, db: Session):
        logger.info("Executing Reservoir Dam Release verification loop...")
        
        source = db.query(Source).filter(Source.name == "Water Resource Management Feed").first()
        if not source:
            source = Source(name="Water Resource Management Feed", url="https://news.google.com/rss/search?q=Tamil+Nadu+dam+release")
            db.add(source)
            db.commit()

        # Query across critical keys
        query_string = " OR ".join(self.DAMS)
        rss_target = f"https://news.google.com/rss/search?q=({query_string})+dam+release+discharge+cusecs&hl=en-IN&gl=IN"
        alerts = self.news_scraper.scrape_media_source(rss_target)

        for alert in alerts:
            # Check if text contains dam release signatures
            contains_dam = any(dam.lower() in alert["title"].lower() for dam in self.DAMS)
            if not contains_dam:
                continue

            district = db.query(District).filter(District.name == alert["district"]).first()
            district_id = district.id if district else None

            if DedupService.is_duplicate(db, "DAM_RELEASE", district_id, alert["district"], "today", alert["title"]):
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
                category="DAM_RELEASE",
                district=alert["district"],
                date_str="Current Hydrological Discharge",
                title=alert["title"],
                content=alert["content"],
                url=alert["url"]
            )
            self.telegram_service.send_channel_message(formatted_msg)