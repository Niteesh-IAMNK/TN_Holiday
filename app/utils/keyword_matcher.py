import re
from loguru import logger

class KeywordMatcher:
    """Linguistic matching component to classify alert contexts and map to functional templates."""

    KEYWORD_MAP = {
        "RAIN_HOLIDAY": [r"heavy\s+rain\s+holiday", r"school\s+holiday", r"colleges?\s+closed", r"rain\s+declared", r"collector\s+announces\s+holiday"],
        "GOVERNMENT_HOLIDAY": [r"public\s+holiday", r"government\s+holiday", r"gazetted\s+holiday", r"restricted\s+holiday"],
        "WEATHER_ALERT": [r"heavy\s+rainfall\s+warning", r"imd\s+alert", r"thunderstorm\s+warn", r"orange\s+alert", r"red\s+alert"],
        "CYCLONE_ALERT": [r"cyclone", r"depression\s+bay\s+of\s+bengal", r"landfall", r"deep\s+depression"],
        "FLOOD_ALERT": [r"flood\s+warning", r"inundation", r"river\s+overflow", r"flooding\s+alert"],
        "DAM_RELEASE": [r"dam\s+open", r"surplus\s+water", r"cusecs\s+released", r"reservoir\s+discharge", r"mttur\s+dam", r"vaigai\s+dam"],
        "ROAD_CLOSURE": [r"traffic\s+diversion", r"road\s+closed", r"landslide\s+block", r"route\s+blocked"],
        "TRANSPORT_ALERT": [r"trains?\s+cancelled", r"buses\s+suspended", r"tnstc\s+status", r"southern\s+railway\s+update"],
        "POWER_ALERT": [r"power\s+shutdown", r"electricity\s+interruption", r"tangedco", r"maintenance\s+shutdown"],
        "EXAM_NOTIFICATION": [r"exams?\s+postponed", r"anna\s+university\s+exam", r"postponement", r"rescheduled\s+date"]
    }

    def __init__(self):
        # Compile pre-calculated byte tracking trees for optimal matching speeds
        self.compiled_map = {
            category: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            for category, patterns in self.KEYWORD_MAP.items()
        }

    def classify_content(self, title: str, content: str = "") -> str:
        """
        Evaluates incoming data signatures against regular expression definitions.
        Returns matching uppercase template key string, falling back to 'EMERGENCY_ALERT'.
        """
        combined_payload = f"{title} {content}"
        
        for category, regex_list in self.compiled_map.items():
            for regex in regex_list:
                if regex.search(combined_payload):
                    logger.info(f"Context analysis match identified category signature target: [{category}]")
                    return category
                    
        return "EMERGENCY_ALERT"