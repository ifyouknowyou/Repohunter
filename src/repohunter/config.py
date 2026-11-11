from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar

import yaml
from pydantic import BaseModel, Field


class GitHubConfig(BaseModel):
    token_env: str = "GITHUB_TOKEN"
    api_timeout: int = 30
    max_retries: int = 3


class StorageConfig(BaseModel):
    research_directory: str = "./RepoHunter_Research"
    max_concurrent_downloads: int = 3


class AnalysisConfig(BaseModel):
    ai_enabled: bool = False
    provider: str | None = None
    model: str | None = None


class SecurityConfig(BaseModel):
    enabled: bool = True
    semgrep_enabled: bool = True
    gitleaks_enabled: bool = True
    osv_enabled: bool = True
    auto_execute_downloaded_code: bool = False


class ReportsConfig(BaseModel):
    default_format: str = "markdown"


class Settings(BaseModel):
    github: GitHubConfig = Field(default_factory=GitHubConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    reports: ReportsConfig = Field(default_factory=ReportsConfig)


class ConfigManager:
    default_paths: ClassVar[list[Path]] = [
        Path.cwd() / "settings.yaml",
        Path.home() / ".config" / "repohunter" / "settings.yaml",
        Path.home() / ".repohunter" / "settings.yaml",
    ]

    @staticmethod
    def _default_settings() -> dict[str, Any]:
        return {
            "github": {"token_env": "GITHUB_TOKEN", "api_timeout": 30, "max_retries": 3},
            "storage": {
                "research_directory": "./RepoHunter_Research",
                "max_concurrent_downloads": 3,
            },
            "analysis": {"ai_enabled": False, "provider": None, "model": None},
            "security": {
                "enabled": True,
                "semgrep_enabled": True,
                "gitleaks_enabled": True,
                "osv_enabled": True,
                "auto_execute_downloaded_code": False,
            },
            "reports": {"default_format": "markdown"},
        }

    @classmethod
    def get_settings_path(cls) -> Path:
        for path in cls.default_paths:
            if path.exists():
                return path
        return cls.default_paths[0]

    @classmethod
    def load_settings(cls) -> Settings:
        path = cls.get_settings_path()
        if not path.exists():
            return Settings()
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        return Settings.model_validate(data)

    @classmethod
    def save_settings(cls, settings: Settings, path: Path | None = None) -> Path:
        target = path or cls.get_settings_path()
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(settings.model_dump(mode="json"), handle, sort_keys=False)
        return target

    @classmethod
    def init_config(cls, path: Path | None = None) -> Path:
        target = path or cls.default_paths[0]
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            return target
        target.write_text(
            yaml.safe_dump(cls._default_settings(), sort_keys=False),
            encoding="utf-8",
        )
        return target
