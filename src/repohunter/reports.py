from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def _prepare_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    prepared: list[dict[str, Any]] = []
    for record in records:
        prepared.append(
            {
                "full_name": record.get("full_name") or record.get("name"),
                "description": record.get("description") or "",
                "language": record.get("language") or record.get("primary_language"),
                "stars": record.get("stargazers_count") or record.get("stars") or 0,
                "forks": record.get("forks_count") or record.get("forks") or 0,
                "quality_score": record.get("quality_score") or 0,
                "category": record.get("category") or "Uncategorized",
                "download_status": record.get("download_status") or "not_downloaded",
                "html_url": record.get("html_url") or "",
            }
        )
    return prepared


def generate_markdown_report(
    records: list[dict[str, Any]], *, title: str = "RepoHunter Report"
) -> str:
    rows = _prepare_records(records)
    lines = [f"# {title}", ""]
    for row in rows:
        lines.append(f"## {row['full_name']}")
        lines.append(f"- Description: {row['description']}")
        lines.append(f"- Language: {row['language']}")
        lines.append(f"- Stars: {row['stars']}")
        lines.append(f"- Forks: {row['forks']}")
        lines.append(f"- Quality score: {row['quality_score']}")
        lines.append(f"- Category: {row['category']}")
        lines.append(f"- Download status: {row['download_status']}")
        lines.append(f"- URL: {row['html_url']}")
        lines.append("")
    return "\n".join(lines)


def generate_json_report(records: list[dict[str, Any]]) -> str:
    return json.dumps(_prepare_records(records), indent=2, sort_keys=True)


def generate_csv_report(records: list[dict[str, Any]], path: str | Path | None = None) -> str:
    rows = _prepare_records(records)
    fieldnames = [
        "full_name",
        "description",
        "language",
        "stars",
        "forks",
        "quality_score",
        "category",
        "download_status",
        "html_url",
    ]
    if path:
        with Path(path).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    return "\n".join(
        ",".join(str(row.get(field, "")) for field in fieldnames)
        for row in [
            {field: field for field in fieldnames},
            *rows,
        ]
    )
