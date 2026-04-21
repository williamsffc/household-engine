from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ScrubResult:
    redacted_text: str
    redaction_counts: dict[str, int]


_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("ssn", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("phone", re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}\b")),
]


def scrub_pii(text: str) -> ScrubResult:
    """Lightweight, layered PII scrubbing (regex-only for Step 5B).

    V1 goal is to ensure text sent to an LLM (later) is meaningfully reduced in risk.
    This is not meant to be perfect; the Review Queue will still show the redacted text.
    """

    redacted = text or ""
    counts: dict[str, int] = {}
    for name, pattern in _PATTERNS:
        redacted, n = pattern.subn(f"[REDACTED_{name.upper()}]", redacted)
        counts[name] = int(n)

    # Redact long numeric identifiers (avoid breaking common dates like 04/07/2026).
    redacted, n = re.subn(r"\b\d{7,}\b", "[REDACTED_ID]", redacted)
    counts["id_like_numbers"] = int(n)

    return ScrubResult(redacted_text=redacted, redaction_counts=counts)
