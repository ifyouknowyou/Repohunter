# RepoHunter CLI

RepoHunter is a local-first GitHub research tool for discovering, evaluating, organizing, and analyzing repositories without automatically downloading or executing source code.

The CLI is designed for security-focused repository discovery workflows such as bug bounty, web security, malware analysis, reverse engineering, cloud security, forensics, and research triage.

## Project goals

- Discover public GitHub repositories from natural-language and topic-based queries
- Collect metadata only by default, with no forced repository cloning during discovery
- Score repositories using transparent heuristics based on activity, docs, license clarity, and relevance
- Store metadata in a local SQLite database for repeatable research workflows
- Organize repositories into local research folders and reports
- Run safe static security scans against downloaded content without executing code
- Produce markdown, JSON, and CSV exports for researchers and workflows

## Installation

From the project root:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
```

Verify the CLI is available:

```bash
repohunter --help
```

## Core workflow

### 1) Discover repositories

```bash
repohunter discover "bug bounty"
repohunter search "web application security" --language Python --min-stars 20 --limit 25
```

### 2) Collect and score repositories

```bash
repohunter collect "security automation" --limit 20 --report --scan --yes
```

This performs discovery, stores results, optionally downloads selected repositories for inspection, and can generate a report.

### 3) Download a specific repo

```bash
repohunter download --repo owner/repository
repohunter download --topic "forensics" --top 5 --limit 20
```

### 4) Inspect local library data

```bash
repohunter library list
repohunter library search "cve"
repohunter library categories
repohunter library info owner/repository
repohunter library export --format json
```

### 5) Produce reports

```bash
repohunter report --format markdown --output RepoHunter_Research/report.md
repohunter report --format json --all
```

### 6) Compare and analyze repositories

```bash
repohunter compare owner/repoA owner/repoB
repohunter analyze owner/repository
```

### 7) Run security scan

```bash
repohunter scan /path/to/downloaded/repo
```

## Configuration

RepoHunter supports a configuration file and environment variables.

Create the default config:

```bash
repohunter config init
```

Or copy the example file manually:

```bash
cp settings.example.yaml settings.yaml
cp .env.example .env
```

Common configuration options include:

- GitHub API token environment variable
- Local research directory
- Storage settings
- Analysis toggles

Use `GITHUB_TOKEN` in the environment or configure the token environment variable in the settings file.

## Doctor check

Run the built-in health check:

```bash
repohunter doctor
```

This checks:

- Python version
- Git availability
- GitHub connectivity
- Writable database path
- Writable storage directory
- Disk space
- GitHub token presence

## Architecture

The project is organized into modular components:

- `repohunter.cli` — terminal entry points and command implementations
- `repohunter.config` — local settings and config management
- `repohunter.db` — SQLite persistence layer
- `repohunter.github_client` — GitHub REST API integration
- `repohunter.search` — discovery, query expansion, and repo normalization
- `repohunter.scoring` — repository quality scoring
- `repohunter.download` — repository cloning and download workflow
- `repohunter.library` — local library search and exports
- `repohunter.organization` — category-based research organization
- `repohunter.security` — static heuristic security scanning
- `repohunter.reports` — markdown/json/csv report generation
- `repohunter.ai` — optional AI-style structured analysis
- `repohunter.utils` — shared helpers

## Safety and assumptions

- This tool is metadata-first by default.
- It does not automatically clone repositories during discovery.
- It does not execute downloaded code.
- Security findings are heuristic and should be treated as signals, not proof.
- GitHub API rate limits and authentication options still matter for large-scale research.

## Commands overview

```bash
repohunter version
repohunter doctor
repohunter search QUERY
repohunter discover QUERY
repohunter download --repo OWNER/REPO
repohunter collect TOPIC --limit 10 --report --scan --yes
repohunter report --format markdown
repohunter compare OWNER/REPO_A OWNER/REPO_B
repohunter analyze OWNER/REPO
repohunter scan /path/to/repo
repohunter config init
repohunter config show
repohunter config set github.token_env GITHUB_TOKEN
repohunter library list
repohunter library search QUERY
repohunter library categories
repohunter library info OWNER/REPO
repohunter library export --format json
```

## License

MIT
