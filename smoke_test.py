import sys
import requests
from loguru import logger
from app.services.message_formatter import MessageFormatter
from app.utils.district_extractor import DistrictExtractor
from app.utils.keyword_matcher import KeywordMatcher

def run_smoke_tests():
    logger.info("Initializing system integration validation checks...")

    # 1. Linguistic Classification Matcher Verification
    matcher = KeywordMatcher()
    category = matcher.classify_content("Heavy downpour recorded, schools closed in coastal regions tomorrow")
    if category == "RAIN_HOLIDAY":
        logger.success("Linguistic classification logic matches keywords accurately.")
    else:
        logger.error(f"Classification failure: Received unexpected category parsing profile [{category}]")
        sys.exit(1)

    # 2. Entity Extraction Vector Verification
    extractor = DistrictExtractor()
    extracted = extractor.extract_district("Emergency notice distributed across Trichy municipal jurisdictions.")
    if extracted == "Tiruchirappalli":
        logger.success("Geographical entity normalization functions properly.")
    else:
        logger.error(f"Entity matching failure: Normalized index mismatch target. Got: [{extracted}]")
        sys.exit(1)

    # 3. HTML Sanitization Filter Verification
    dirty_title = "<script>alert('hazard')</script> Safe Notice & Headline"
    clean_html = MessageFormatter.sanitize_input(dirty_title)
    if "&lt;script&gt;" in clean_html:
        logger.success("XSS sanitation rules work. Malicious payloads correctly escaped.")
    else:
        logger.error("XSS escaping failure. Vulnerabilities detected in string manipulation layout.")
        sys.exit(1)

    logger.success("All micro-service test profiles passed successfully.")

if __name__ == "__main__":
    run_smoke_tests()