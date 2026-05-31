import re

# Regex patterns for Indian PII
PII_PATTERNS = {
    "PAN": r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b",
    "Aadhaar": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
    "Phone": r"\b(?:\+91|91)?[\s-]?[6789]\d{9}\b",
    "Email": r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
}

# Simple heuristic keywords for advisory or subjective intent
ADVISORY_KEYWORDS = [
    "should i invest", "best fund", "recommend", "which is better", 
    "good time to buy", "will it go up", "price prediction", 
    "suggest a fund", "top mutual funds", "advise me", "is it good",
    "what should i buy", "where should i invest", "which fund to pick"
]

def check_pii(text: str) -> bool:
    """Returns True if PII is detected in the text."""
    for key, pattern in PII_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            return True
            
    # Stricter OTP check: Look for the word OTP near a number to avoid false positive on normal numbers
    if re.search(r"\botp\b.*\b\d{4,6}\b", text, re.IGNORECASE):
        return True
        
    return False

def check_advisory_intent(text: str) -> bool:
    """Returns True if the query is asking for subjective financial advice."""
    text_lower = text.lower()
    for keyword in ADVISORY_KEYWORDS:
        if keyword in text_lower:
            return True
    return False
