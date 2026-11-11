from __future__ import annotations

from typing import Any


class AIAnalysisProvider:
    def __init__(self, enabled: bool = False) -> None:
        self.enabled = enabled

    def analyze(self, repository: dict[str, Any]) -> str:
        if not self.enabled:
            return (
                "AI analysis not enabled. Set analysis.ai_enabled to true and configure a provider."
            )
        name = repository.get("full_name") or repository.get("name") or "unknown"
        description = repository.get("description") or "No description provided."
        language = repository.get("language") or repository.get("primary_language") or "Unknown"
        stars = repository.get("stargazers_count") or repository.get("stars") or 0
        updated = repository.get("updated_at") or "unknown"
        return (
            f"AI analysis for {name}: Purpose appears aligned with security/research workflows. "
            f"Primary language: {language}. Description: {description}. "
            f"Community interest: {stars} stars. Maintenance signal: last updated {updated}. "
            "Review dependency risk, security posture, and installation requirements before use."
        )


def structured_ai_analysis(repository: dict[str, Any]) -> dict[str, Any]:
    name = repository.get("full_name") or repository.get("name") or "unknown"
    language = repository.get("language") or repository.get("primary_language") or "Unknown"
    description = repository.get("description") or "No description available."
    stars = repository.get("stargazers_count") or repository.get("stars") or 0
    topics = repository.get("topics") or []
    return {
        "repository": name,
        "purpose": "Research-oriented tooling or security utility",
        "main_features": [
            "Repository discovery and source inspection",
            "Security-focused analysis",
        ],
        "technologies_used": [language, *([str(item) for item in topics[:4]] if topics else [])],
        "installation_requirements": "Review README before installation; do not execute setup scripts automatically.",
        "documentation_quality": "Check README and release notes before use.",
        "maintenance_indicators": f"Stars: {stars}; updated_at={repository.get('updated_at', 'unknown')}",
        "security_concerns": "Review dependency versions and installation scripts before use.",
        "research_applications": "Use for repository intelligence, security comparisons, and local analysis.",
        "summary": f"{name} appears relevant to security research; description: {description}",
    }
