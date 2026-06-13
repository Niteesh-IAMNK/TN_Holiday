import hashlib
from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session
from app.database.models import Alert

class DedupService:
    """Calculates systemic signature keys and cross-references active records to prevent message double-delivery."""

    @staticmethod
    def generate_hash(category: str, district: str, date_str: str, title: str) -> str:
        """
        Generates a SHA-256 hex string profile tracking distinct variable keys:
        category + district + date + title
        """
        # Formulate strict predictable structures by cleaning case strings
        norm_category = str(category).strip().lower()
        norm_district = str(district).strip().lower()
        norm_date = str(date_str).strip().lower()
        norm_title = str(title).strip().lower()

        raw_payload = f"{norm_category}|{norm_district}|{norm_date}|{norm_title}"
        return hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()

    @classmethod
    def is_duplicate(cls, db: Session, category: str, district_id: int | None, district_name: str, date_str: str, title: str) -> bool:
        """
        Cross-references the calculated hash key with historical alert objects inside the MariaDB lifecycle.
        """
        calculated_hash = cls.generate_hash(category, district_name, date_str, title)
        logger.debug(f"Computed de-duplication signature verification: {calculated_hash}")

        # Construct target bounds to verify whether identical content patterns exist in the pipeline
        query = db.query(Alert).filter(
            Alert.title == title.strip()
        )
        
        if district_id:
            query = query.filter(Alert.district_id == district_id)
        else:
            query = query.filter(Alert.district_id.is_(None))

        existing_alerts = query.all()

        for alert in existing_alerts:
            # Reconstruct signatures to handle raw historic values securely
            historical_district_name = alert.district.name if alert.district else "statewide"
            historic_date_str = alert.published_at.strftime("%Y-%m-%d")
            
            historic_hash = cls.generate_hash(category, historical_district_name, historic_date_str, alert.title)
            if calculated_hash == historic_hash:
                logger.warning(f"Duplicate structural record detected matching signature sequence identity hash: {calculated_hash}")
                return True

        return False