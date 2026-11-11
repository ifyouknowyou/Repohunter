from __future__ import annotations

from typer.testing import CliRunner

from repohunter.cli import app
from repohunter.scoring import score_repository
from repohunter.search import expand_query

runner = CliRunner()


def test_version_command():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.output.strip()


def test_search_expansion():
    expanded = expand_query("bug bounty")
    assert "bug bounty" in expanded
    assert "reconnaissance tools" in expanded


def test_quality_score_range():
    repo = {
        "description": "Security tooling",
        "updated_at": "2025-01-12T00:00:00Z",
        "stargazers_count": 120,
        "forks_count": 40,
        "license": {"spdx_id": "MIT"},
        "language": "Python",
        "topics": ["security"],
        "archived": False,
    }
    result = score_repository(repo)
    assert 0 <= result["total"] <= 100
    assert result["breakdown"]["license_clarity"] >= 10


def test_config_init_creates_file(tmp_path):
    path = tmp_path / "settings.yaml"
    from repohunter.config import ConfigManager

    created = ConfigManager.init_config(path)
    assert created.exists()
    content = path.read_text(encoding="utf-8")
    assert "github:" in content


def test_report_generation(tmp_path):
    from repohunter.reports import generate_markdown_report

    report = generate_markdown_report(
        [
            {
                "full_name": "owner/repo",
                "description": "Example reproducible project",
                "language": "Python",
                "stargazers_count": 12,
                "forks_count": 2,
                "quality_score": 85,
                "category": "Uncategorized",
                "download_status": "downloaded",
                "html_url": "https://example.com",
            }
        ]
    )
    assert "owner/repo" in report
    assert "Quality score: 85" in report


def test_scan_repository(tmp_path):
    from repohunter.security import scan_repository

    repo = tmp_path / "sample"
    repo.mkdir()
    (repo / "secret.txt").write_text("AWS_SECRET_ACCESS_KEY=abcd\n", encoding="utf-8")
    findings = scan_repository(str(repo))
    assert findings


def test_report_output_creates_parent_directory(tmp_path):
    output_path = tmp_path / "nested" / "report.md"
    result = runner.invoke(app, ["report", "--format", "markdown", "--output", str(output_path)])
    assert result.exit_code == 0
    assert output_path.exists()
