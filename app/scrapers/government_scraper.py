from bs4 import BeautifulSoup
from loguru import logger
from app.scrapers.web_scraper import WebScraper
from app.utils.district_extractor import DistrictExtractor
from app.utils.keyword_matcher import KeywordMatcher

class GovernmentScraper(WebScraper):
    """Directly scrapes government portal tables and announcement feeds."""

    def __init__(self):
        super().__init__(cache_expire_seconds=300) # Lower cache windows for high-priority government channels
        self.district_engine = DistrictExtractor()
        self.keyword_engine = KeywordMatcher()

    def scrape_press_releases(self, target_portal_url: str) -> list[dict]:
        """
        Directly parses announcements from government press release portals.
        Utilizes BeautifulSoup for robust navigation of legacy HTML layouts.
        """
        results = []
        html_payload = self.fetch_url(target_portal_url, use_cache=False) # Always fresh for government alerts

        if not html_payload:
            logger.error(f"Failed to access government portal endpoint: {target_portal_url}")
            return results

        try:
            soup = BeautifulSoup(html_payload, "lxml")
            
            # Target common elements found in typical government bulletin layouts (e.g., table rows or list cards)
            listings = soup.find_all("tr") or soup.find_all("li") or soup.find_all("div", class_="views-row")
            
            for item in listings:
                anchor = item.find("a")
                if not anchor or not anchor.get("href"):
                    continue
                    
                title_text = anchor.get_text(strip=True)
                relative_url = anchor.get("href")
                
                # Resolve relative links
                absolute_url = relative_url if relative_url.startswith("http") else f"{target_portal_url.rstrip('/')}/{relative_url.lstrip('/')}"
                
                # Extract text snippets from container rows if available
                snippet_text = item.get_text(strip=True)

                if len(title_text) > 10:  # Filter out noise elements
                    detected_district = self.district_engine.extract_district(title_text)
                    assigned_category = self.keyword_engine.classify_content(title_text, snippet_text)
                    
                    results.append({
                        "title": title_text,
                        "url": absolute_url,
                        "content": snippet_text,
                        "district": detected_district if detected_district else "Statewide",
                        "category": assigned_category,
                        "source_type": "GOVERNMENT_PORTAL"
                    })
                    
            logger.info(f"Extracted ({len(results)}) valid release points from government portal structure layout.")
        except Exception as e:
            logger.error(f"Error encountered parsing raw government portal markup elements: {e}")

        return results