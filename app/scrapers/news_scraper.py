from loguru import logger
from app.scrapers.rss_scraper import RssScraper
from app.scrapers.html_parser import HtmlParser
from app.utils.district_extractor import DistrictExtractor
from app.utils.keyword_matcher import KeywordMatcher

class NewsScraper:
    """Orchestrates high-level processing pipelines across commercial Tamil media feeds."""

    def __init__(self):
        self.rss_engine = RssScraper()
        self.district_engine = DistrictExtractor()
        self.keyword_engine = KeywordMatcher()

    def scrape_media_source(self, rss_endpoint: str) -> list[dict]:
        """
        Scrapes a news media channel, runs natural language classification, 
        and extracts geographical properties.
        """
        processed_alerts = []
        raw_items = self.rss_engine.parse_feed(rss_endpoint)

        for item in raw_items:
            # Clean summaries using fallback tools if complex elements are found
            clean_text_content = HtmlParser.extract_text_by_selector(f"<div>{item['raw_content']}</div>", "div")
            if not clean_text_content:
                clean_text_content = item['raw_content']

            # Extract entities
            detected_district = self.district_engine.extract_district(f"{item['title']} {clean_text_content}")
            assigned_category = self.keyword_engine.classify_content(item['title'], clean_text_content)

            processed_alerts.append({
                "title": item['title'],
                "url": item['url'],
                "content": clean_text_content,
                "district": detected_district if detected_district else "Statewide",
                "category": assigned_category,
                "published_raw": item['published_raw']
            })

        return processed_alerts