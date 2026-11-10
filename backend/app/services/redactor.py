"""
Credential & PII Redactor
Uses pre-compiled regular expressions to strip high-entropy API keys, tokens, and credentials.
"""

import re

# High-entropy credential patterns
PATTERNS = [
    # OpenAI API Key
    (re.compile(r"sk-[a-zA-Z0-9]{32,64}"), "[REDACTED_OPENAI_KEY]"),
    # GitHub Personal Access Token
    (re.compile(r"ghp_[a-zA-Z0-9]{36}"), "[REDACTED_GITHUB_TOKEN]"),
    # AWS Access Key ID
    (re.compile(r"AKIA[0-9A-Z]{16}"), "[REDACTED_AWS_KEY]"),
    # Generic JWT Token
    (re.compile(r"eyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}"), "[REDACTED_JWT_TOKEN]"),
]


def sanitize_content(text: str) -> str:
    """Replaces sensitive credential patterns with redacted placeholders."""
    if not text:
        return ""
    sanitized = text
    for pattern, replacement in PATTERNS:
        sanitized = pattern.sub(replacement, sanitized)
    return sanitized


# Alias for backward compatibility
sanitize_credentials = sanitize_content

