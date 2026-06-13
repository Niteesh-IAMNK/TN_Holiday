from sqlalchemy.orm import Session
from loguru import logger
from app.scrapers.news_scraper import NewsScraper
from app.services.dedup_service import DedupService
from app.services.message_formatter import MessageFormatter
from app.services.telegram_service import TelegramService
from app.database.models import Alert, District, Source, PriorityEnum

class RoadClosureService:
    HIGH_USAGE_ROADS = [
        "OMR", "ECR", "GST Road", "Anna Salai", "Poonamallee High Road",
        "Inner Ring Road", "Chennai Bypass", "Chennai-Bengaluru Highway",
        "Chennai-Trichy Highway", "Madurai Ring Road"
    ]

    def __init__(self):
        self.scraper = NewsScraper()
        self.telegram = TelegramService()

    def process_closures(self, db: Session):
        logger.info("Scanning arterial road networks for disruptions...")
        source = db.query(Source).filter(Source.name == "Traffic Media Streams").first()
        if not source:
            source = Source(name="Traffic Media Streams", url="https://news.google.com")
            db.add(source)
            db.commit()

        query_roads = " OR ".join([f'"{road}"' for road in self.HIGH_USAGE_ROADS])
        rss_url = f"https://news.google.com/rss/search?q=({query_roads})+traffic+closure+diversion+block&hl=en-IN&gl=IN"
        
        alerts = self.scraper.scrape_media_source(rss_url)
        for alert in alerts:
            matched_road = next((road for road in self.HIGH_USAGE_ROADS if road.lower() in alert["title"].lower() or road.lower() in alert["content"].lower()), None)
            if not matched_road:
                continue

            district = db.query(District).filter(District.name == alert["district"]).first()
            district_id = district.id if district else None

            if DedupService.is_duplicate(db, "ROAD_CLOSURE", district_id, alert["district"], "today", alert["title"]):
                continue

            new_alert = Alert(
                title=f"[{matched_road}] {alert['title']}", content=alert["content"], source_id=source.id,
                district_id=district_id, priority=PriorityEnum.MEDIUM, raw_url=alert["url"],
                published_at=__import__('datetime').datetime.utcnow()
            )
            db.add(new_alert)
            db.commit()

            msg = MessageFormatter.format_message("ROAD_CLOSURE", alert["district"], "Active Layout Window", new_alert.title, alert["content"], alert["url"])
            self.telegram.send_channel_message(msg)