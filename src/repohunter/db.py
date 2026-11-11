from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy import Boolean, Column, Float, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from repohunter.config import ConfigManager


class Base(DeclarativeBase):
    pass


class RepositoryRecord(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True)
    owner = Column(String, nullable=False)
    repo_name = Column(String, nullable=False)
    full_name = Column(String, unique=True, nullable=False)
    description = Column(String)
    html_url = Column(String)
    primary_language = Column(String)
    stars = Column(Integer, default=0)
    forks = Column(Integer, default=0)
    open_issues = Column(Integer, default=0)
    license_name = Column(String)
    created_at = Column(String)
    updated_at = Column(String)
    archived = Column(Boolean, default=False)
    topics = Column(String)
    readme_available = Column(Boolean, default=False)
    quality_score = Column(Float, default=0.0)
    category = Column(String, default="Uncategorized")
    local_path = Column(String)
    download_status = Column(String, default="not_downloaded")
    last_checked = Column(String)
    ai_summary = Column(String)
    security_status = Column(String)
    default_branch = Column(String)
    repository_size = Column(Integer, default=0)
    record_metadata = Column(String)


class DatabaseManager:
    def __init__(self, database_path: str | Path | None = None) -> None:
        ConfigManager.load_settings()
        target = (
            Path(database_path) if database_path else Path.home() / ".repohunter" / "repohunter.db"
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        self.database_path = str(target)
        self.engine = create_engine(f"sqlite:///{self.database_path}")
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def upsert_repository(self, repository: dict[str, Any]) -> RepositoryRecord:
        with self.SessionLocal() as session:
            existing = (
                session.query(RepositoryRecord).filter_by(full_name=repository["full_name"]).first()
            )
            if existing is None:
                record = RepositoryRecord(**self._record_from_dict(repository))
                session.add(record)
            else:
                for key, value in self._record_from_dict(repository).items():
                    setattr(existing, key, value)
                record = existing
            session.commit()
            session.refresh(record)
            return record

    def list_repositories(self, limit: int = 50) -> list[RepositoryRecord]:
        with self.SessionLocal() as session:
            return (
                session.query(RepositoryRecord)
                .order_by(RepositoryRecord.id.desc())
                .limit(limit)
                .all()
            )

    def search(self, query: str) -> list[RepositoryRecord]:
        q = f"%{query.lower()}%"
        with self.SessionLocal() as session:
            return (
                session.query(RepositoryRecord)
                .filter(
                    (RepositoryRecord.full_name.ilike(q))
                    | (RepositoryRecord.description.ilike(q))
                    | (RepositoryRecord.primary_language.ilike(q))
                    | (RepositoryRecord.category.ilike(q))
                )
                .order_by(RepositoryRecord.quality_score.desc())
                .all()
            )

    def _record_from_dict(self, repository: dict[str, Any]) -> dict[str, Any]:
        return {
            "owner": repository.get("owner", "unknown"),
            "repo_name": repository.get("name", repository.get("repo_name", "unknown")),
            "full_name": repository.get("full_name")
            or f"{repository.get('owner', 'unknown')}/{repository.get('name', 'unknown')}",
            "description": repository.get("description"),
            "html_url": repository.get("html_url") or repository.get("url"),
            "primary_language": repository.get("language") or repository.get("primary_language"),
            "stars": int(repository.get("stargazers_count") or 0),
            "forks": int(repository.get("forks_count") or 0),
            "open_issues": int(repository.get("open_issues_count") or 0),
            "license_name": (repository.get("license") or {}).get("spdx_id")
            if isinstance(repository.get("license"), dict)
            else repository.get("license_name"),
            "created_at": repository.get("created_at"),
            "updated_at": repository.get("updated_at") or repository.get("pushed_at"),
            "archived": bool(repository.get("archived") or False),
            "topics": ", ".join(repository.get("topics") or []),
            "readme_available": bool(repository.get("readme_available") or False),
            "quality_score": float(repository.get("quality_score") or 0.0),
            "category": repository.get("category") or "Uncategorized",
            "local_path": repository.get("local_path"),
            "download_status": repository.get("download_status") or "not_downloaded",
            "last_checked": repository.get("last_checked"),
            "ai_summary": repository.get("ai_summary"),
            "security_status": repository.get("security_status") or "not_scanned",
            "default_branch": repository.get("default_branch"),
            "repository_size": int(
                repository.get("size") or repository.get("repository_size") or 0
            ),
            "record_metadata": json.dumps(repository.get("metadata") or repository),
        }
