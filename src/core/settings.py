from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Runtime settings (intentionally lightweight; no external deps)."""

    allow_remote: bool = False


def _parse_bool(value: str | None, *, default: bool = False) -> bool:
    if value is None:
        return default
    v = value.strip().lower()
    return v in {"1", "true", "yes", "y", "on"}


def get_settings() -> Settings:
    # Local-first default: reject non-loopback requests unless explicitly allowed.
    return Settings(allow_remote=_parse_bool(os.getenv("HOUSEHOLD_ALLOW_REMOTE"), default=False))
