from loguru import logger
from selectolax.parser import HTMLParser as FastParser

class HtmlParser:
    """High-performance structural extractor using selectolax (C-based performance parsing)."""

    @staticmethod
    def extract_text_by_selector(html_content: str, selector: str) -> str:
        """Extracts text content from a single element matching a CSS selector."""
        if not html_content:
            return ""
        try:
            tree = FastParser(html_content)
            node = tree.css_first(selector)
            if node:
                return node.text(strip=True)
        except Exception as e:
            logger.error(f"Selectolax native parser exception triggered under CSS rule selector '{selector}': {e}")
        return ""

    @staticmethod
    def extract_links(html_content: str, selector: str = "a") -> list[str]:
        """Extracts href values matching a specified CSS selector."""
        links = []
        if not html_content:
            return links
        try:
            tree = FastParser(html_content)
            for node in tree.css(selector):
                href = node.attributes.get("href")
                if href:
                    links.append(href.strip())
        except Exception as e:
            logger.error(f"Error extracting anchor arrays under selector layout engine context: {e}")
        return links