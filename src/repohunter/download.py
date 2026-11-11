from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from repohunter.config import ConfigManager


def download_repository(
    repo_full_name: str, *, destination_root: str | Path | None = None, shallow: bool = True
) -> str:
    settings = ConfigManager.load_settings()
    root = Path(destination_root) if destination_root else Path(settings.storage.research_directory)
    root.mkdir(parents=True, exist_ok=True)
    safe_name = repo_full_name.replace("/", "__")
    destination = root / safe_name
    if destination.exists():
        return str(destination)
    if shutil.which("git") is None:
        raise RuntimeError("Git is not installed or not available on PATH")
    args = ["git", "clone", f"https://github.com/{repo_full_name}.git", str(destination)]
    if shallow:
        args.insert(2, "--depth")
        args.insert(3, "1")
    completed = subprocess.run(args, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(
            f"Git clone failed for {repo_full_name}: {completed.stderr[:500]} or {completed.stdout[:500]}"
        )
    return str(destination)


def estimate_download_size(repositories: list[dict[str, Any]]) -> int:
    total = 0
    for repo in repositories:
        size_mb = int(repo.get("size") or 0)
        total += max(size_mb, 20)
    return total
