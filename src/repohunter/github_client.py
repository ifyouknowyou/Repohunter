from __future__ import annotations

import os
from typing import Any

import httpx

from repohunter.config import ConfigManager


class GitHubClient:
    def __init__(self, token: str | None = None) -> None:
        settings = ConfigManager.load_settings()
        self.token = token or os.getenv(settings.github.token_env) or os.getenv("GITHUB_TOKEN")
        self.timeout = settings.github.api_timeout
        self.max_retries = settings.github.max_retries
        self.base_url = "https://api.github.com"

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "RepoHunter/0.1.0"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        last_exc: Exception | None = None
        for _ in range(self.max_retries):
            try:
                response = httpx.request(
                    method, url, timeout=self.timeout, headers=self._headers(), **kwargs
                )
                if response.status_code == 429:
                    raise RuntimeError("GitHub API rate limit reached")
                if response.status_code == 401:
                    raise PermissionError("Invalid GitHub token or unauthorized request")
                return response
            except (httpx.HTTPError, PermissionError, RuntimeError) as exc:
                last_exc = exc
        if last_exc:
            raise last_exc
        raise RuntimeError("GitHub request failed")

    def search_repositories(
        self,
        query: str,
        *,
        language: str | None = None,
        min_stars: int = 0,
        per_page: int = 10,
        page: int = 1,
        include_archived: bool = False,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": per_page,
            "page": page,
        }
        if language:
            params["language"] = language
        if min_stars:
            params["q"] = f"{params['q']} stars:>={min_stars}"
        if not include_archived:
            params["q"] = f"{params['q']} archived:false"
        response = self._request("GET", f"{self.base_url}/search/repositories", params=params)
        if response.status_code >= 400:
            raise RuntimeError(f"GitHub API request failed: {response.text[:200]}")
        payload = response.json()
        return payload.get("items", [])

    def get_repository(self, full_name: str) -> dict[str, Any]:
        response = self._request("GET", f"{self.base_url}/repos/{full_name}")
        if response.status_code >= 400:
            raise RuntimeError(f"Unable to fetch repository metadata: {response.text[:200]}")
        return response.json()
