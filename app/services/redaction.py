import re

PATTERNS = [
    (r'(?i)(authorization\s*:\s*bearer\s+)[A-Za-z0-9._-]+', r'\1********'),
    (r'(?i)(password\s*[=:]\s*)[^\s]+', r'\1********'),
    (r'(?i)(token\s*[=:]\s*)[^\s]+', r'\1********'),
    (r'(?i)(api[_-]?key\s*[=:]\s*)[^\s]+', r'\1********'),
    (r'\bAKIA[0-9A-Z]{16}\b', 'AWS_ACCESS_KEY_REDACTED'),
]

def redact(text: str) -> str:
    for pattern, replacement in PATTERNS:
        text = re.sub(pattern, replacement, text)
    return text
