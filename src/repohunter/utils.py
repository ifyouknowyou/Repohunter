from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_directory(path: str | Path) -> Path:
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def dedupe_by_full_name(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for item in items:
        full_name = str(item.get("full_name") or item.get("fullName") or "").strip()
        if not full_name or full_name in seen:
            continue
        seen.add(full_name)
        deduped.append(item)
    return deduped
