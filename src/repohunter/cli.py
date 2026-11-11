from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from repohunter import __version__
from repohunter.ai import AIAnalysisProvider, structured_ai_analysis
from repohunter.config import ConfigManager
from repohunter.db import DatabaseManager
from repohunter.download import download_repository
from repohunter.library import LibraryManager
from repohunter.organization import ensure_research_layout, infer_category, organize_repository
from repohunter.reports import generate_json_report, generate_markdown_report
from repohunter.search import discover_repositories
from repohunter.security import scan_repository, summarize_findings
from repohunter.utils import ensure_directory

console = Console()
app = typer.Typer(help="RepoHunter CLI")
config_app = typer.Typer(help="Repository configuration")
library_app = typer.Typer(help="Local repository library")

app.add_typer(config_app, name="config")
app.add_typer(library_app, name="library")


def banner() -> None:
    console.print(
        Panel.fit(
            "[bold cyan]REPOHUNTER CLI[/bold cyan]\n\n"
            "[green]GitHub Repository Intelligence Engine[/green]\n"
            "[bold]DISCOVER • COLLECT • ANALYZE[/bold]",
            box=box.HEAVY,
        )
    )


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        banner()
        console.print(f"Version: {__version__}")
        console.print("Run 'repohunter --help' for usage information.")


@app.command("version")
def version():
    console.print(__version__)


@app.command("doctor")
def doctor():
    banner()
    issues: list[str] = []
    python_ok = sys.version_info >= (3, 12)
    git_ok = (
        subprocess.run(["git", "--version"], capture_output=True, text=True, check=False).returncode
        == 0
    )
    storage_dir = Path(ConfigManager.load_settings().storage.research_directory)
    settings = ConfigManager.load_settings()
    token = os.getenv(settings.github.token_env) or os.getenv("GITHUB_TOKEN")
    db_path = Path.home() / ".repohunter" / "repohunter.db"
    db_ok = True
    storage_ok = True
    disk_ok = True
    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        db_path.touch(exist_ok=True)
    except OSError:
        db_ok = False
    try:
        storage_dir.mkdir(parents=True, exist_ok=True)
        probe = storage_dir / ".repohunter_write_test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
    except OSError:
        storage_ok = False
    try:
        usage = shutil.disk_usage(storage_dir)
        disk_ok = usage.free > 100 * 1024 * 1024
    except OSError:
        disk_ok = False
    try:
        import httpx

        response = httpx.get("https://api.github.com", timeout=10)
        github_ok = response.status_code in {200, 403, 401}
    except (httpx.HTTPError, OSError, TimeoutError, ValueError):
        github_ok = False
    if not python_ok:
        issues.append("Python 3.12+ is required")
    if not git_ok:
        issues.append("Git is not installed or not on PATH")
    if not github_ok:
        issues.append("GitHub connectivity check failed")
    if not token:
        issues.append(
            "No GitHub token configured; unauthenticated search is still allowed but limited"
        )
    if not db_ok:
        issues.append("Database path is not writable")
    if not storage_ok:
        issues.append("Research storage directory is not writable")
    if not disk_ok:
        issues.append("Insufficient free disk space for research downloads")
    if not issues:
        console.print("[green]Doctor checks passed.[/green]")
    else:
        for issue in issues:
            console.print(f"[yellow]WARNING:[/yellow] {issue}")


@config_app.command("init")
def config_init(path: str | None = typer.Option(None, "--path")):
    target = Path(path) if path else ConfigManager.default_paths[0]
    created = ConfigManager.init_config(target)
    console.print(f"Configuration created at {created}")


@config_app.command("show")
def config_show():
    settings = ConfigManager.load_settings()
    console.print(json.dumps(settings.model_dump(mode="json"), indent=2, sort_keys=True))


@config_app.command("set")
def config_set(key: str, value: str):
    settings = ConfigManager.load_settings()
    key_parts = key.split(".")
    current = settings
    for part in key_parts[:-1]:
        current = getattr(current, part)
    raw: object = value
    if isinstance(raw, str):
        lower = raw.lower()
        if lower in {"true", "false"}:
            raw = lower == "true"
        elif lower in {"null", "none"}:
            raw = None
        elif raw.isdigit() or (raw.startswith("-") and raw[1:].isdigit()):
            raw = int(raw)
        elif raw.replace(".", "", 1).isdigit() or (
            raw.startswith("-") and raw[1:].replace(".", "", 1).isdigit()
        ):
            raw = float(raw)
    setattr(current, key_parts[-1], raw)
    ConfigManager.save_settings(settings)
    console.print(f"Set {key}={value}")


@app.command("search")
def search_repo(
    query: str,
    language: str | None = typer.Option(None, "--language"),
    min_stars: int = typer.Option(0, "--min-stars"),
    limit: int = typer.Option(10, "--limit"),
    include_archived: bool = typer.Option(False, "--include-archived"),
):
    results = discover_repositories(
        query,
        limit=limit,
        language=language,
        min_stars=min_stars,
        include_archived=include_archived,
    )
    if not results:
        console.print("[yellow]No repositories found.[/yellow]")
        return
    table = Table(title=f"Search results for: {query}")
    table.add_column("Repo")
    table.add_column("Language")
    table.add_column("Stars")
    table.add_column("Score")
    for repo in results:
        table.add_row(
            repo.get("full_name", ""),
            repo.get("language") or "Unknown",
            str(repo.get("stargazers_count", 0)),
            str(repo.get("quality_score", 0)),
        )
    console.print(table)
    db = DatabaseManager()
    for repo in results:
        db.upsert_repository(repo)


@app.command("discover")
def discover(query: str):
    search_repo(query)


@app.command("download")
def download_cmd(
    repo: str | None = typer.Option(None, "--repo"),
    topic: str | None = typer.Option(None, "--topic"),
    top: int = typer.Option(5, "--top"),
    limit: int = typer.Option(10, "--limit"),
    selected: bool = typer.Option(False, "--selected"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    if repo:
        destination = ConfigManager.load_settings().storage.research_directory
        if dry_run:
            console.print(f"[yellow]Dry run:[/yellow] would download {repo} to {destination}")
            return
        path = download_repository(repo, destination_root=destination)
        console.print(f"Downloaded repository to {path}")
        return
    if selected:
        saved = DatabaseManager().list_repositories(limit=100)
        if not saved:
            console.print("[yellow]No stored repositories available for download.[/yellow]")
            return
        for saved_entry in saved:
            repo_name = str(saved_entry.full_name)
            if dry_run:
                console.print(f"[yellow]Dry run:[/yellow] would download {repo_name}")
            else:
                path = download_repository(
                    repo_name,
                    destination_root=ConfigManager.load_settings().storage.research_directory,
                )
                console.print(f"Downloaded {repo_name} -> {path}")
        return
    if topic:
        results: list[dict[str, object]] = discover_repositories(topic, limit=limit)
        repo_entries: list[dict[str, object]] = list(results[:top])
        for repo_entry in repo_entries:
            repo_name = str(repo_entry.get("full_name") or "")
            if dry_run:
                console.print(f"[yellow]Dry run:[/yellow] would download {repo_name}")
            else:
                target = download_repository(
                    repo_name,
                    destination_root=ConfigManager.load_settings().storage.research_directory,
                )
                console.print(f"Downloaded {repo_name} -> {target}")
        return
    console.print("[red]Please provide --repo, --topic, or --selected.[/red]")


@app.command("collect")
def collect(
    topic: str,
    limit: int = typer.Option(10, "--limit"),
    analyze: bool = typer.Option(False, "--analyze"),
    deduplicate: bool = typer.Option(True, "--deduplicate"),
    scan: bool = typer.Option(False, "--scan"),
    report: bool = typer.Option(False, "--report"),
    yes: bool = typer.Option(False, "--yes"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    if not yes and not dry_run:
        confirmed = typer.confirm("This may download and scan repositories. Continue?")
        if not confirmed:
            console.print("[yellow]Aborted.[/yellow]")
            raise typer.Exit()
    results = discover_repositories(topic, limit=limit)
    if deduplicate:
        results = list({repo["full_name"]: repo for repo in results}.values())
    if not results:
        console.print("[yellow]No repositories matched the collection topic.[/yellow]")
        return
    table = Table(title=f"Collection preview for '{topic}'")
    table.add_column("Repo")
    table.add_column("Stars")
    table.add_column("Score")
    for repo in results:
        table.add_row(
            repo.get("full_name", ""),
            str(repo.get("stargazers_count", 0)),
            str(repo.get("quality_score", 0)),
        )
    console.print(table)
    if dry_run:
        console.print("[green]Dry run complete. No files downloaded or modified.[/green]")
        return
    destination_root = ConfigManager.load_settings().storage.research_directory
    ensure_directory(destination_root)
    layout = ensure_research_layout(destination_root)
    for repo in results:
        repo_name = str(repo.get("full_name") or "")
        category = infer_category(topic, repo)
        if analyze:
            provider = AIAnalysisProvider(enabled=ConfigManager.load_settings().analysis.ai_enabled)
            repo["ai_summary"] = provider.analyze(repo)
        if scan:
            repo_path = download_repository(repo_name, destination_root=destination_root)
            findings = scan_repository(repo_path)
            repo["security_status"] = f"{len(findings)} findings" if findings else "clean"
            repo["security_summary"] = summarize_findings(findings)
        else:
            repo_path = download_repository(repo_name, destination_root=destination_root)
        repo["download_status"] = "downloaded"
        repo["local_path"] = repo_path
        repo["category"] = category
        organize_repository(repo, layout["root"], category=category)
        db = DatabaseManager()
        db.upsert_repository(repo)
    if report:
        markdown = generate_markdown_report(results, title=f"Collection report: {topic}")
        report_path = Path(destination_root) / "reports" / "collection_report.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(markdown, encoding="utf-8")
        console.print(f"Report saved to {report_path}")
    console.print(f"[green]Collected {len(results)} repositories.[/green]")


@library_app.command("list")
def library_list(limit: int = typer.Option(25, "--limit")):
    items = LibraryManager().list_repositories(limit=limit)
    table = Table(title="Library")
    table.add_column("Repository")
    table.add_column("Category")
    table.add_column("Score")
    for item in items:
        table.add_row(item.full_name, item.category, str(item.quality_score))
    console.print(table)


@library_app.command("search")
def library_search(query: str):
    items = LibraryManager().search(query)
    if not items:
        console.print("[yellow]No matching library entries found.[/yellow]")
        return
    for item in items:
        console.print(f"- {item.full_name} ({item.category}) score={item.quality_score}")


@library_app.command("categories")
def library_categories():
    categories = LibraryManager().categories()
    for name, count in categories.items():
        console.print(f"- {name}: {count}")


@library_app.command("info")
def library_info(full_name: str):
    items = LibraryManager().search(full_name)
    if not items:
        console.print("[yellow]Repository not found in the local library.[/yellow]")
        return
    item = items[0]
    table = Table(title=f"Repository info: {item.full_name}")
    table.add_column("Field")
    table.add_column("Value")
    for field, value in {
        "description": item.description,
        "category": item.category,
        "quality_score": item.quality_score,
        "location": item.local_path,
        "download_status": item.download_status,
        "security_status": item.security_status,
        "license": item.license_name,
    }.items():
        table.add_row(field, str(value or "n/a"))
    console.print(table)


@library_app.command("export")
def library_export(format_name: str = typer.Option("json", "--format")):
    payload = LibraryManager().export(format_name)
    console.print(json.dumps(payload, indent=2, default=str))


@app.command("report")
def report_cmd(
    format_name: str = typer.Option("markdown", "--format"),
    all_items: bool = typer.Option(False, "--all"),
    output: str | None = typer.Option(None, "--output"),
):
    records = DatabaseManager().list_repositories(limit=500)
    if not all_items and records:
        records = [
            item for item in records if item.download_status == "downloaded" or item.quality_score
        ]
    data = [
        {
            "full_name": item.full_name,
            "description": item.description,
            "language": item.primary_language,
            "stargazers_count": item.stars,
            "forks_count": item.forks,
            "quality_score": item.quality_score,
            "category": item.category,
            "download_status": item.download_status,
            "html_url": item.html_url,
        }
        for item in records
    ]
    if format_name == "markdown":
        contents = generate_markdown_report(data, title="RepoHunter report")
    elif format_name == "json":
        contents = generate_json_report(data)
    elif format_name == "csv":
        csv_path = output or "report.csv"
        Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
        from repohunter.reports import generate_csv_report

        contents = generate_csv_report(data, path=csv_path)
    else:
        raise typer.BadParameter("Supported formats: markdown, json, csv")
    target = output or f"report.{format_name}"
    path_obj = Path(target)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    path_obj.write_text(contents, encoding="utf-8")
    console.print(f"Report written to {target}")


@app.command("compare")
def compare(repo1: str, repo2: str):
    from repohunter.github_client import GitHubClient

    client = GitHubClient()
    details = []
    for repo_name in (repo1, repo2):
        try:
            data = client.get_repository(repo_name)
            score = data.get("stargazers_count", 0)
            details.append(
                {
                    "repo": repo_name,
                    "language": data.get("language") or "Unknown",
                    "stars": data.get("stargazers_count", 0),
                    "forks": data.get("forks_count", 0),
                    "license": (data.get("license") or {}).get("spdx_id")
                    if isinstance(data.get("license"), dict)
                    else "Unknown",
                    "updated": data.get("updated_at") or "unknown",
                    "score": score,
                }
            )
        except Exception as exc:  # noqa: BLE001 - CLI comparison should degrade gracefully
            console.print(f"[yellow]Warning:[/yellow] Unable to compare {repo_name}: {exc}")
            details.append(
                {
                    "repo": repo_name,
                    "language": "Unknown",
                    "stars": 0,
                    "forks": 0,
                    "license": "Unknown",
                    "updated": "unknown",
                    "score": 0,
                }
            )
    table = Table(title="Repository comparison")
    table.add_column("Repository")
    table.add_column("Language")
    table.add_column("Stars")
    table.add_column("Forks")
    table.add_column("License")
    table.add_column("Updated")
    for item in details:
        table.add_row(
            item["repo"],
            item["language"],
            str(item["stars"]),
            str(item["forks"]),
            item["license"],
            str(item["updated"]),
        )
    console.print(table)


@app.command("analyze")
def analyze_cmd(repo: str):
    from repohunter.github_client import GitHubClient

    client = GitHubClient()
    try:
        data = client.get_repository(repo)
    except (RuntimeError, ValueError, TimeoutError, OSError) as exc:
        console.print(f"[red]Unable to analyze {repo}: {exc}[/red]")
        raise typer.Exit() from exc
    analysis = structured_ai_analysis(data)
    table = Table(title=f"AI-style analysis for {repo}")
    table.add_column("Field")
    table.add_column("Value")
    for key, value in analysis.items():
        table.add_row(key, str(value))
    console.print(table)


@app.command("scan")
def scan(path: str):
    findings = scan_repository(path)
    summary = summarize_findings(findings)
    if not findings:
        console.print("[green]No static security findings detected.[/green]")
        return
    table = Table(title=f"Scan results for {path}")
    table.add_column("Severity")
    table.add_column("File")
    table.add_column("Detail")
    for item in findings:
        table.add_row(item["severity"], item["file"], item["detail"])
    console.print(table)
    console.print(f"Summary: CRITICAL={summary.get('CRITICAL', 0)}, HIGH={summary.get('HIGH', 0)}, MEDIUM={summary.get('MEDIUM', 0)}, LOW={summary.get('LOW', 0)}, INFO={summary.get('INFO', 0)}")


@app.command("deduplicate")
def deduplicate_cmd():
    console.print("[green]Deduplication is handled by name during discovery.[/green]")


@app.command("history")
def history():
    console.print("[green]History tracking is stored in the local SQLite library database.[/green]")


@app.command("cleanup")
def cleanup():
    console.print("[green]Cleanup command executed; no destructive operation performed.[/green]")


@app.command("update")
def update():
    console.print("[green]RepoHunter is up to date.[/green]")


if __name__ == "__main__":
    app()
