from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        return datetime.fromisoformat(normalized).astimezone(UTC)
    except ValueError:
        return None


def score_repository(repo: dict[str, Any]) -> dict[str, Any]:
    now = datetime.now(UTC)
    updated_at = parse_date(repo.get("updated_at") or repo.get("pushed_at"))
    maintenance_points = 25
    if updated_at is None:
        maintenance_points = 5
    else:
        age_days = (now - updated_at).total_seconds() / 86400
        if age_days < 30:
            maintenance_points = 25
        elif age_days < 180:
            maintenance_points = 18
        elif age_days < 365:
            maintenance_points = 10
        else:
            maintenance_points = 5

    description = (repo.get("description") or "").strip()
    docs_points = 20 if description else 8
    if repo.get("readme_available"):
        docs_points = min(docs_points + 5, 25)

    stars = int(repo.get("stargazers_count") or 0)
    forks = int(repo.get("forks_count") or 0)
    community_points = min(15, 5 + min(stars, 150) / 20 + min(forks, 100) / 10)

    license_points = (
        10 if (repo.get("license") or {}).get("spdx_id") or repo.get("license_name") else 0
    )
    project_points = 15 if repo.get("language") else 8
    if repo.get("topics"):
        project_points += 3
    project_points = min(project_points, 18)

    relevance = 15 if stars > 0 or description else 5

    total = round(
        maintenance_points
        + docs_points
        + community_points
        + license_points
        + project_points
        + relevance
    )
    total = max(0, min(100, total))

    return {
        "total": total,
        "breakdown": {
            "maintenance_activity": round(maintenance_points),
            "documentation_quality": round(docs_points),
            "community_engagement": round(community_points),
            "license_clarity": license_points,
            "project_completeness": round(project_points),
            "technical_relevance": relevance,
        },
        "maintained": updated_at is not None and (now - updated_at).total_seconds() / 86400 < 365,
        "archived": bool(repo.get("archived") or False),
    }
