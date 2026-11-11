from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from repohunter.utils import ensure_directory, utc_now_iso

CATEGORY_KEYWORDS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("bug bounty", "bugbounty", "reconnaissance", "vulnerability research"), "01_Bug_Bounty"),
    (("penetration testing", "pentest", "red team", "exploitation"), "02_Penetration_Testing"),
    (("web security", "webapp", "application security", "owasp"), "03_Web_Security"),
    (("network security", "networking", "packet analysis", "wifi"), "04_Network_Security"),
    (("cve", "vulnerability disclosure", "security advisory"), "05_CVE_Research"),
    (("digital forensics", "forensics", "incident response"), "06_Digital_Forensics"),
    (("security automation", "automation", "devsecops"), "07_Security_Automation"),
    (("malware", "malware analysis", "reverse engineering"), "08_Malware_Analysis"),
    (("cloud security", "cloud", "kubernetes", "aws security"), "09_Cloud_Security"),
    (("reverse engineering", "binary analysis", "assembly"), "10_Reverse_Engineering"),
)


def infer_category(topic: str | None, repository: dict[str, Any] | None = None) -> str:
    text_parts: list[str] = []
    if topic:
        text_parts.append(topic)
    if repository:
        text_parts.append(str(repository.get("description") or ""))
        text_parts.extend(str(item) for item in repository.get("topics") or [])
    combined = " ".join(text_parts).lower()
    for keywords, folder in CATEGORY_KEYWORDS:
        if any(keyword in combined for keyword in keywords):
            return folder
    return "Uncategorized"


def ensure_research_layout(root: str | Path) -> dict[str, Path]:
    root_path = Path(root)
    layout = {
        "root": root_path,
        "categories": root_path / "categories",
        "metadata": root_path / "metadata",
        "reports": root_path / "reports",
        "reports_markdown": root_path / "reports" / "markdown",
        "reports_json": root_path / "reports" / "json",
        "reports_csv": root_path / "reports" / "csv",
        "logs": root_path / "logs",
        "database": root_path / "database",
    }
    for path in layout.values():
        ensure_directory(path)
    return layout


def organize_repository(
    repository: dict[str, Any],
    root: str | Path,
    *,
    category: str | None = None,
) -> dict[str, str]:
    root_path = Path(root)
    category_name = category or infer_category(repository.get("metadata", {}).get("topic"), repository)
    repo_key = str(repository.get("full_name") or repository.get("name") or "repository")
    repo_dir_name = repo_key.replace("/", "__")
    category_dir = root_path / "categories" / category_name
    repo_dir = category_dir / repo_dir_name
    ensure_directory(repo_dir)
    metadata = {
        "repository": repo_key,
        "category": category_name,
        "downloaded_at": utc_now_iso(),
        "description": repository.get("description"),
        "language": repository.get("language") or repository.get("primary_language"),
        "quality_score": repository.get("quality_score"),
        "download_status": repository.get("download_status", "not_downloaded"),
        "local_path": str(repo_dir),
        "html_url": repository.get("html_url") or "",
        "topics": repository.get("topics") or [],
    }
    metadata_path = repo_dir / "repository_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")
    return {
        "category": category_name,
        "folder": str(repo_dir),
        "metadata_path": str(metadata_path),
    }
