from __future__ import annotations

from repohunter.db import DatabaseManager


class LibraryManager:
    def __init__(self, db: DatabaseManager | None = None) -> None:
        self.db = db or DatabaseManager()

    def list_repositories(self, limit: int = 25):
        return self.db.list_repositories(limit=limit)

    def search(self, query: str):
        return self.db.search(query)

    def categories(self):
        items = self.db.list_repositories(limit=500)
        categories: dict[str, int] = {}
        for item in items:
            key = item.category or "Uncategorized"
            categories[key] = categories.get(key, 0) + 1
        return categories

    def export(self, format_name: str = "json"):
        records = self.db.list_repositories(limit=500)
        if format_name == "json":
            return [
                {
                    "full_name": r.full_name,
                    "description": r.description,
                    "category": r.category,
                    "download_status": r.download_status,
                    "quality_score": r.quality_score,
                    "local_path": r.local_path,
                }
                for r in records
            ]
        return records
