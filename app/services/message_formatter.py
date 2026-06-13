import html
from loguru import logger
from app.utils.message_templates import TEMPLATES

class MessageFormatter:
    """Escapes raw dynamic strings and injects sanitized inputs into core Telegram structures."""

    @staticmethod
    def sanitize_input(text: str | None) -> str:
        """Escapes special structural XML/HTML components to safely render inside Telegram."""
        if not text:
            return ""
        return html.escape(str(text).strip())

    @classmethod
    def format_message(cls, category: str, district: str, date_str: str, title: str, content: str, url: str | None) -> str:
        """
        Builds a production-ready HTML message payload based on a predefined category string template.
        """
        template_key = category.upper().strip()
        if template_key not in TEMPLATES:
            logger.warning(f"Category pattern '{template_key}' unknown. Falling back to EMERGENCY_ALERT schema layout.")
            template_key = "EMERGENCY_ALERT"

        raw_template = TEMPLATES[template_key]

        # Sanitize internal attributes without destroying structural anchor tags
        clean_district = cls.sanitize_input(district)
        clean_date = cls.sanitize_input(date_str)
        clean_title = cls.sanitize_input(title)
        clean_content = cls.sanitize_input(content)
        clean_url = url if url else "https://www.tn.gov.in"

        try:
            return raw_template.format(
                district=clean_district,
                date=clean_date,
                title=clean_title,
                content=clean_content,
                url=clean_url
            )
        except KeyError as e:
            logger.error(f"Failed to populate template formatting blocks due to a missing mapping key: {e}")
            raise ValueError(f"Formatting failed for template parameters key sequence: {e}")