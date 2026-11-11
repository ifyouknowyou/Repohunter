from __future__ import annotations

from typing import Any

from repohunter.github_client import GitHubClient
from repohunter.scoring import score_repository
from repohunter.utils import dedupe_by_full_name


def expand_query(topic: str) -> list[str]:
    topic_clean = topic.strip()
    if not topic_clean:
        return []
    base = [topic_clean]
    expansions = {
        "bug bounty": [
            "bug bounty automation",
            "web security testing",
            "reconnaissance tools",
            "vulnerability research",
            "responsible disclosure",
            "security testing frameworks",
        ],
        "security": ["security tools", "cybersecurity research", "security automation"],
        "forensics": ["digital forensics tools", "incident response"],
        "network": ["network security analysis", "packet analysis tools"],
    }
    expansions_map = expansions.get(topic_clean.lower(), [])
    return list(dict.fromkeys(base + expansions_map))


def build_repo_payload(
    repo: dict[str, Any],
    *,
    category: str = "Uncategorized",
    topic: str | None = None,
    default_quality: int = 0,
) -> dict[str, Any]:
    quality = score_repository(repo)
    total = quality["total"] if quality else default_quality
    record = {
        "full_name": repo.get("full_name"),
        "name": repo.get("name"),
        "owner": repo.get("owner", {}).get("login")
        if isinstance(repo.get("owner"), dict)
        else "unknown",
        "description": repo.get("description"),
        "html_url": repo.get("html_url"),
        "language": repo.get("language"),
        "stargazers_count": repo.get("stargazers_count", 0),
        "forks_count": repo.get("forks_count", 0),
        "open_issues_count": repo.get("open_issues_count", 0),
        "license": repo.get("license"),
        "created_at": repo.get("created_at"),
        "updated_at": repo.get("updated_at") or repo.get("pushed_at"),
        "archived": bool(repo.get("archived") or False),
        "topics": repo.get("topics", []),
        "readme_available": bool(repo.get("readme_available") or False),
        "default_branch": repo.get("default_branch"),
        "size": repo.get("size", 0),
        "quality_score": total,
        "category": category,
        "download_status": "not_downloaded",
        "quality_breakdown": quality.get("breakdown", {}),
        "metadata": {
            "topic": topic,
            "quality": quality,
            "available_fields": list(repo.keys()),
        },
    }
    return record


def discover_repositories(
    topic: str,
    *,
    limit: int = 10,
    language: str | None = None,
    min_stars: int = 0,
    include_archived: bool = False,
) -> list[dict[str, Any]]:
    client = GitHubClient()
    collected: list[dict[str, Any]] = []
    for query in expand_query(topic):
        try:
            batch = client.search_repositories(
                query,
                language=language,
                min_stars=min_stars,
                per_page=min(limit, 10),
                include_archived=include_archived,
            )
        except (RuntimeError, PermissionError):
            continue
        for repo in batch:
            repo_payload = build_repo_payload(repo, category="Uncategorized", topic=topic)
            collected.append(repo_payload)
        if len(collected) >= limit:
            break
    deduped = dedupe_by_full_name(collected)
    return deduped[:limit]
