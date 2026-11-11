from __future__ import annotations

import hashlib
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_directory(path: str | Path) -> Path:
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def normalize_full_name(owner: str, repo_name: str) -> str:
    return f"{owner.strip()}/{repo_name.strip()}".strip("/")


def default_research_directory() -> Path:
    return Path.cwd() / "RepoHunter_Research"


def git_available() -> bool:
    return shutil.which("git") is not None


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


def safe_json_dumps(data: Any) -> str:
    return json.dumps(data, sort_keys=True, default=str)


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]
