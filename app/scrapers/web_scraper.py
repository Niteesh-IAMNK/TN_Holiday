import time
import requests
from loguru import logger
from diskcache import Cache
from app.config import settings

class WebScraper:
    """Base structural web scraper with integrated custom user-agents, caching, and smart retries."""

    def __init__(self, cache_expire_seconds: int = 900):
        # Cache artifacts inside target scratch directories
        self.cache = Cache(str(settings.BASE_DIR / "data" / "cache"))
        self.cache_expiry = cache_expire_seconds
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        })

    def fetch_url(self, url: str, use_cache: bool = True, retries: int = 3, timeout: int = 15) -> str | None:
        """Fetches HTML string payloads from network endpoints with adaptive backoff."""
        if use_cache:
            cached_data = self.cache.get(url)
            if cached_data:
                logger.debug(f"Cache hit verified for target resource URL structure: {url}")
                return cached_data

        backoff = 2.0
        for attempt in range(1, retries + 1):
            try:
                logger.info(f"Request outbound target -> Attempt ({attempt}/{retries}): {url}")
                response = self.session.get(url, timeout=timeout)
                
                # Check server error codes immediately
                response.raise_for_status()
                
                html_payload = response.text
                if use_cache:
                    self.cache.set(url, html_payload, expire=self.cache_expiry)
                return html_payload

            except requests.exceptions.HTTPError as e:
                logger.warning(f"Server issued standard rejection HTTP error structure: {e}")
                if response.status_code in [403, 404]:
                    break # Unrecoverable authorization/existence path blocks
            except requests.exceptions.RequestException as e:
                logger.error(f"Network transport degradation caught: {e}. Postponing line queue...")
            
            if attempt < retries:
                time.sleep(backoff)
                backoff *= 2
                
        logger.error(f"Failed to fetch content from resource endpoint after full retry loop: {url}")
        return None