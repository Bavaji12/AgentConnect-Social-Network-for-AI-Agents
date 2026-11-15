import re
from typing import Tuple

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"disregard\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"you\s+are\s+now\s+(an?\s+)?unrestricted",
    r"system\s*:\s*override",
    r"bypass\s+all\s+(filters|rules|restrictions)",
    r"developer\s+mode\s+enabled",
    r"forget\s+(everything|all\s+rules)",
    r"print\s+(your\s+)?(system\s+prompt|instructions)",
    r"reveal\s+(your\s+)?(api[_\s-]?key|secret)",
    r"<script\b",
    r"javascript\s*:",
]

COMPILED_INJECTION_REGEX = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]

def detect_prompt_injection(text: str) -> Tuple[bool, str]:
    """
    Scans text for prompt injection attempts, system instruction overrides,
    and adversarial jailbreak attempts.
    Returns: (is_injection_detected: bool, reason: str)
    """
    if not text:
        return False, ""

    for pattern in COMPILED_INJECTION_REGEX:
        match = pattern.search(text)
        if match:
            return True, f"Suspicious instruction override detected matching pattern: '{match.group(0)}'"

    return False, ""

def sanitize_untrusted_text(text: str) -> str:
    """
    Cleans untrusted user / post content to neutralize control sequences.
    """
    if not text:
        return ""
    # Strip null bytes and non-printable control characters (keep newlines/tabs)
    sanitized = "".join(ch for ch in text if ch in "\n\r\t" or 32 <= ord(ch) <= 126 or ord(ch) > 127)
    return sanitized.strip()

def validate_llm_output(content: str) -> Tuple[bool, str]:
    """
    Validates autonomous LLM response before publishing it as an official comment.
    Prevents empty responses, system prompt leakages, and inappropriate content.
    """
    if not content or len(content.strip()) < 5:
        return False, "Generated comment is empty or too short."

    # Check for leaked secrets or system prompt markers
    lower = content.lower()
    if "system:" in lower or "api_key" in lower or "bearer " in lower or "jwt_secret" in lower:
        return False, "Generated comment contains sensitive system or credential keywords."

    if any(p.search(content) for p in COMPILED_INJECTION_REGEX):
        return False, "Generated comment contains echoed instruction injection phrases."

    return True, "Valid"
