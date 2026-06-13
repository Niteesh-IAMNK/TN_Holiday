import feedparser
from loguru import logger
from app.scrapers.web_scraper import WebScraper

class RssScraper(WebScraper):
    """Parses syndication feeds to extract structured news and notification updates."""

    def parse_feed(self, feed_url: str) -> list[dict]:
        """
        Parses remote RSS feeds.
        Returns a structured list of normalized dictionary payloads.
        """
        # Fetch raw data using base web scraper to leverage caching and custom user-agents
        raw_xml = self.fetch_url(feed_url, use_cache=True)
        entries_summary = []

        if not raw_xml:
            logger.error(f"Aborting parsing due to raw XML content delivery failure on URL: {feed_url}")
            return entries_summary

        try:
            parsed_feed = feedparser.parse(raw_xml)
            if parsed_feed.bozo:
                logger.warning(f"Feedparser identified non-well-formed XML formatting metrics in feed: {feed_url}")

            for entry in parsed_feed.entries:
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                summary = entry.get("summary", entry.get("description", "")).strip()
                published = entry.get("published", entry.get("updated", None))

                if title and link:
                    entries_summary.append({
                        "title": title,
                        "url": link,
                        "raw_content": summary,
                        "published_raw": published
                    })

            logger.info(f"Extracted ({len(entries_summary)}) structured data items from RSS Feed endpoint channel.")
        except Exception as e:
            logger.critical(f"Fatal parser breakdown during parsing of syndication source matrix: {e}")
            
        return entries_summary