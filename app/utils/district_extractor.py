import re
from loguru import logger

class DistrictExtractor:
    """Uses specialized regular expressions to isolate Tamil Nadu districts from raw unstructured text."""
    
    # Official 38 districts of Tamil Nadu
    DISTRICTS = [
        "Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore", 
        "Dharmapuri", "Dindigul", "Erode", "Kallakurichi", "Kanchipuram", 
        "Kanyakumari", "Karur", "Krishnagiri", "Madurai", "Mayiladuthurai", 
        "Nagapattinam", "Namakkal", "Nilgiris", "Perambalur", "Pudukkottai", 
        "Ramanathapuram", "Ranipet", "Salem", "Sivaganga", "Tenkasi", 
        "Thanjavur", "Theni", "Thoothukudi", "Tiruchirappalli", "Tirunelveli", 
        "Tirupathur", "Tiruppur", "Tiruvallur", "Tiruvannamalai", "Tiruvarur", 
        "Vellore", "Viluppuram", "Virudhunagar"
    ]

    def __init__(self):
        # Compile case-insensitive boundary regex engines for precision matching
        self.patterns = {
            district: re.compile(rf'\b{re.escape(district)}\b', re.IGNORECASE)
            for district in self.DISTRICTS
        }
        
        # Common alternate representations or localized shorthand
        self.aliases = {
            "Trichy": "Tiruchirappalli",
            "Tuticorin": "Thoothukudi",
            "Ooty": "Nilgiris",
            "The Nilgiris": "Nilgiris",
            "Madras": "Chennai",
            "Kovai": "Coimbatore"
        }
        self.alias_patterns = {
            alias: re.compile(rf'\b{re.escape(alias)}\b', re.IGNORECASE)
            for alias in self.aliases
        }

    def extract_district(self, text: str) -> str | None:
        """
        Scans free-form text blocks. Returns the first matched standard district name, 
        or None if it appears state-wide or indeterminate.
        """
        if not text:
            return None

        # Standard check
        for district, pattern in self.patterns.items():
            if pattern.search(text):
                logger.debug(f"Direct spatial vector match discovered: [{district}]")
                return district

        # Alias conversion check
        for alias, target_district in self.alias_patterns.items():
            if _pattern := self.alias_patterns[alias].search(text):
                logger.debug(f"Alias string variant match discovered: [{alias}] maps to [{target_district}]")
                return target_district

        return None