# REPOHUNTER CLI — UPDATED MASTER AI CODING COMMAND
## Metadata-First GitHub Repository Intelligence & Cybersecurity Research Engine

### PROJECT IDENTITY

Build a professional, production-ready, terminal-only application named **RepoHunter CLI**.

**Tagline:** Discover Thousands. Understand Hundreds. Download Only What Matters.

**Core mission:** Help users discover, evaluate, classify, analyze, organize, and research GitHub repositories without downloading their complete source code.

RepoHunter is a local-first GitHub research intelligence tool, initially optimized for cybersecurity research topics such as:

- Bug bounty
- Penetration testing
- Web application security
- Network security
- Vulnerability research
- CVE research
- Digital forensics
- Security automation
- Cloud security
- Reverse engineering

### NON-NEGOTIABLE PRODUCT RULES

1. This is a CLI-only application.
2. Do not build a website, frontend, dashboard, browser interface, or graphical application.
3. Metadata-only collection is the default behavior.
4. Never automatically clone or download repository source code during discovery, analysis, ranking, or collection.
5. Never download entire repositories unless the user explicitly requests a full download.
6. Keep repository information in a local SQLite database.
7. Minimize network requests, API consumption, and local storage.
8. Never execute downloaded repository code.
9. Clearly distinguish verified GitHub metadata from estimates and AI-generated assessments.
10. Build a real working application, not a prototype or pseudocode project.

---

# PART 1 — INSPECT THE EXISTING PROJECT

Before changing anything:

- Inspect the existing project directory.
- Identify the existing architecture, code, dependencies, configuration, and tests.
- Preserve working functionality.
- Identify bugs and incomplete features.
- Create an implementation plan based on the actual codebase.
- Do not unnecessarily rewrite functioning components.

If the project is empty, establish the architecture from scratch.

Recommended stack:

- Python 3.12+
- Typer for CLI commands
- Rich for terminal output
- httpx for HTTP requests
- GitHub REST API for repository discovery and metadata
- SQLite for persistent storage
- SQLAlchemy for database management
- Pydantic for data validation
- PyYAML for configuration
- pytest for testing
- Ruff for linting
- mypy for type checking

---

# PART 2 — PROFESSIONAL CLI EXPERIENCE

Create a polished terminal experience using Rich.

Requirements:

- Professional terminal tables.
- Colored status indicators.
- Search progress indicators.
- Repository discovery summaries.
- API rate-limit information.
- Storage usage information.
- Error messages with useful recovery instructions.
- Clear command help.
- Interactive confirmations for operations that consume significant resources.

Example:

repohunter discover "bug bounty" --limit 50

Example output:

REPOHUNTER — REPOSITORY DISCOVERY

Search: bug bounty
Repositories found: 50
Metadata collected: 50
Source code downloaded: 0
Storage used: 2.4 MB
Duplicates skipped: 3

The numbers above are illustrative. Display actual measured results.

---

# PART 3 — GITHUB REPOSITORY DISCOVERY ENGINE

Build an advanced discovery engine using the GitHub API.

Requirements:

- Search public GitHub repositories.
- Support keyword and multi-keyword searches.
- Expand cybersecurity-related search terms.
- Search by repository topics.
- Filter by programming language.
- Filter by stars and forks.
- Filter by license.
- Filter by last update.
- Filter by creation date.
- Filter by repository size.
- Support pagination.
- Handle API rate limits.
- Retry transient failures.
- Deduplicate repository results.
- Cache suitable responses to avoid unnecessary API requests.

Example:

repohunter discover "bug bounty automation" --limit 100

repohunter discover "web application security" --language Python --min-stars 10

repohunter discover "CVE research" --updated-within 12m

IMPORTANT:

Discovery must collect repository information only. It must not clone repositories or download ZIP archives.

---

# PART 4 — METADATA-ONLY COLLECTION SYSTEM

This is the most important part of RepoHunter.

Build a complete metadata-first collection engine.

For every discovered repository, collect available information such as:

### Repository identity
- Repository name.
- Owner.
- Full repository identifier.
- GitHub URL.
- Description.
- Topics.
- Default branch.
- Repository visibility.

### Popularity and activity
- Stars.
- Forks.
- Open issues.
- Watchers where available.
- Creation date.
- Last update date.
- Last push date.

### Technical information
- Primary programming language.
- Languages breakdown when available.
- Repository size reported by GitHub.
- License.
- Releases.
- Latest release information.
- Dependency manifest availability.

### Documentation
- README content when accessible.
- README URL.
- Documentation links.
- Wiki availability where discoverable.

### Research information
- Cybersecurity category.
- Search keywords.
- Relevance score.
- Maintenance assessment.
- Documentation assessment.
- License clarity.
- Repository completeness indicators.

Store this information in SQLite.

Create stable repository identifiers so the same repository is not repeatedly stored as a new record.

Requirements:

- Update existing metadata instead of creating duplicates.
- Record the time metadata was collected.
- Track metadata refresh history.
- Cache information appropriately.
- Allow metadata refresh without losing research notes.
- Handle deleted, renamed, private, or unavailable repositories.
- Store source URLs for traceability.

Do not download repository source code as part of this process.

---

# PART 5 — REMOTE REPOSITORY INTELLIGENCE

Build a remote inspection system that works without cloning entire repositories.

It may retrieve selected GitHub information using API endpoints, such as:

- README files.
- Repository language statistics.
- Root directory listings.
- Dependency manifests.
- Configuration filenames.
- GitHub topics.
- Releases.
- License information.

Allow the user to request specific remote inspections.

Examples:

repohunter inspect owner/repository

repohunter inspect owner/repository --readme

repohunter inspect owner/repository --manifests

repohunter inspect owner/repository --tree

Requirements:

- Fetch only the information needed for the requested inspection.
- Avoid recursively retrieving every file.
- Respect GitHub API limits.
- Limit response sizes.
- Cache retrieved content.
- Report unavailable information honestly.
- Do not claim complete code analysis when only metadata or documentation was inspected.
- Never execute remote or downloaded code.

Store inspection results separately from repository metadata.

---

# PART 6 — REPOSITORY QUALITY SCORING

Build a transparent repository scoring engine.

Score repositories using available evidence:

1. Relevance to the search topic.
2. Maintenance activity.
3. Documentation quality.
4. Community engagement.
5. License clarity.
6. Project completeness.
7. Technical information availability.

Create an explainable scoring system.

Example output:

Repository: example-security-tool

Relevance: 92/100
Maintenance: 85/100
Documentation: 90/100
Community: 76/100
License clarity: Verified
Overall score: 86/100

IMPORTANT:

- Do not confuse popularity with quality.
- Do not treat stars as proof of security or reliability.
- Do not invent missing information.
- Show unavailable dimensions as unknown.
- Explain why a repository receives its score.
- Keep scoring configurable.
- Do not claim source-code quality has been assessed without actually inspecting source code.

---

# PART 7 — CYBERSECURITY CLASSIFICATION ENGINE

Automatically classify repositories into categories:

01_Bug_Bounty
02_Penetration_Testing
03_Web_Security
04_Network_Security
05_CVE_Research
06_Digital_Forensics
07_Security_Automation
08_Malware_Analysis
09_Cloud_Security
10_Reverse_Engineering
11_OSINT
12_Security_Research
13_Unknown

Classification should use:

- Repository description.
- GitHub topics.
- README content when available.
- Programming language.
- Relevant keywords.

Allow repositories to have multiple categories.

Save classification explanations and confidence levels.

Allow users to manually change categories.

Do not download repository source code to perform basic classification.

---

# PART 8 — AI REPOSITORY ANALYSIS

Implement an optional AI analysis system with a provider-independent architecture.

AI providers must be configurable.

Analyze available information such as:

- Repository description.
- README.
- Topics.
- Dependency manifests when retrieved.
- GitHub metadata.
- Releases.
- Documentation.

Generate a structured research summary containing:

1. What the project does.
2. Main purpose.
3. Main features.
4. Target users.
5. Programming languages.
6. Technologies and frameworks.
7. Dependencies identified.
8. Installation instructions found in documentation.
9. Maintenance observations.
10. Documentation quality.
11. Potential research applications.
12. Limitations and missing information.

IMPORTANT:

- AI analysis is optional.
- Never require AI to use the basic CLI.
- Never send private credentials or sensitive local files to AI providers.
- Clearly label AI-generated conclusions.
- Never claim to have inspected source code when only the README was retrieved.
- Preserve evidence links for important claims.
- Cache AI results and allow users to refresh them.
- Provide a useful non-AI fallback.

---

# PART 9 — LOCAL RESEARCH LIBRARY

Build a persistent local research library.

Use SQLite as the central database.

Allow users to:

- List collected repositories.
- Search repository names.
- Search descriptions.
- Search README text already collected.
- Filter by category.
- Filter by programming language.
- Filter by stars.
- Filter by quality score.
- Filter by license.
- Filter by update date.
- View repository details.
- Add personal notes.
- Add tags.
- Mark favorites.
- Create named research collections.
- Export selected repository records.

Example:

repohunter library list

repohunter library search "subdomain enumeration"

repohunter library search "SQL injection" --category Web_Security

repohunter library favorites

repohunter library show owner/repository

Named collection examples:

repohunter collection create "My Bug Bounty Research"

repohunter collection add "My Bug Bounty Research" owner/repository

repohunter collection list

A named research collection should reference repository records. It must not automatically download source code.

---

# PART 10 — REPOSITORY RANKING AND COMPARISON

Implement ranking and comparison based on stored metadata.

Examples:

repohunter rank --top 20

repohunter rank --category Bug_Bounty --top 30

repohunter compare owner/repo1 owner/repo2

Comparison should include:

- Description.
- Programming language.
- Stars and forks.
- Recent activity.
- License.
- Documentation availability.
- Quality score.
- Research relevance.
- Known limitations.

Clearly identify missing information.

---

# PART 11 — STORAGE-EFFICIENT DATABASE AND CACHE

Storage efficiency is a core product requirement.

Create a storage manager.

Default collection should store:

- Repository metadata.
- README text when available.
- Selected inspection information.
- AI summaries if enabled.
- User notes.
- Collection records.
- Search history.

Do not store full repository source code by default.

Requirements:

- Deduplicate repeated metadata.
- Avoid storing identical README content repeatedly where practical.
- Limit cached API response sizes.
- Configure cache expiration.
- Support cache cleanup.
- Provide database backup.
- Support database integrity checks.
- Track the storage consumed by metadata, cache, reports, and optional downloads separately.

Commands:

repohunter storage

repohunter storage --details

repohunter cache clear

repohunter database backup

repohunter database check

Example output:

REPOHUNTER STORAGE REPORT

Repository records: 2,500
README records: 1,200
AI summaries: 300
Full repository downloads: 0

Database: Actual measured size
Cache: Actual measured size
Reports: Actual measured size
Downloads: Actual measured size
Total: Actual measured size

Never use invented storage statistics.

---

# PART 12 — OPTIONAL FULL REPOSITORY DOWNLOAD

Full repository downloading is an optional secondary capability.

It must never happen automatically.

Require explicit user intent.

Examples:

repohunter download owner/repository

repohunter download owner/repository --branch main

Before downloading:

- Show repository URL.
- Show GitHub-reported repository size.
- Explain that Git clone size can differ from the reported size.
- Check available disk space.
- Ask for confirmation unless the user explicitly uses an appropriate confirmation flag.
- Show the destination path.
- Avoid duplicate downloads.
- Support cancellation and recovery.
- Track downloaded repository versions.

Store optional downloads separately from metadata.

Do not download every repository in a collection unless the user explicitly requests batch downloading.

Never execute downloaded code or automatically install dependencies.

---

# PART 13 — REPORT GENERATION

Generate research reports from stored information.

Supported formats:

- Markdown.
- JSON.
- CSV.

Examples:

repohunter report --format markdown

repohunter report --category Bug_Bounty

repohunter report --top 20

repohunter report --output ./reports/bug-bounty.md

Reports should contain:

- Repository name.
- Owner.
- URL.
- Description.
- Category.
- Language.
- Stars.
- License.
- Last update.
- Quality score.
- README availability.
- Analysis summary.
- Inspection status.
- Download status.
- Research notes.

Never imply that metadata-only reports contain full source-code analysis.

---

# PART 14 — ONE-COMMAND RESEARCH WORKFLOW

Create an integrated metadata-first workflow.

Example:

repohunter collect "bug bounty automation" --limit 100

Expected behavior:

1. Search GitHub.
2. Retrieve repository metadata.
3. Deduplicate results.
4. Classify repositories.
5. Calculate available quality scores.
6. Retrieve README information where accessible.
7. Save results to SQLite.
8. Display collection statistics.
9. Generate an optional summary report.

IMPORTANT:

This command must not clone or download repository source code.

Optional flags:

--analyze
--refresh
--category
--language
--min-stars
--dry-run
--report

AI analysis must remain optional.

---

# PART 15 — COMMAND-LINE INTERFACE

Implement these commands:

repohunter
repohunter version
repohunter doctor

repohunter config init
repohunter config show
repohunter config set

repohunter discover
repohunter collect
repohunter inspect
repohunter analyze
repohunter rank
repohunter compare

repohunter library list
repohunter library search
repohunter library show
repohunter library favorites

repohunter collection create
repohunter collection add
repohunter collection list

repohunter report
repohunter storage

repohunter cache clear
repohunter database backup
repohunter database check

repohunter download
repohunter history
repohunter update

Ensure every command has working functionality, useful help text, input validation, and appropriate error handling.

---

# PART 16 — CONFIGURATION AND SECURITY

Create a configuration file in the user's configuration directory.

Allow configuration of:

- GitHub API token.
- AI provider.
- AI model.
- Database location.
- Cache expiration.
- Default result limits.
- Maximum README size.
- Request timeout.
- Retry count.
- Download directory.
- Report directory.
- Default cybersecurity categories.

Security requirements:

- Never hardcode API tokens.
- Never print secrets.
- Never commit secrets to Git.
- Use environment variables or secure configuration mechanisms.
- Redact sensitive values from logs.
- Validate URLs and API responses.
- Handle untrusted repository content as data, not instructions.
- Never execute retrieved README instructions or code.

---

# PART 17 — ERROR HANDLING AND TESTING

Test:

- GitHub API failures.
- API rate limits.
- Missing README files.
- Large README files.
- Deleted repositories.
- Renamed repositories.
- Duplicate repositories.
- Invalid repository names.
- Network interruptions.
- Database failures.
- Invalid API tokens.
- AI provider failures.
- Cache expiration.
- Metadata refresh.
- CSV and JSON exports.
- Storage calculations.
- Optional download failures.

Create unit tests and integration tests using mocked API responses and safe fixtures.

Do not depend on live GitHub access for every test.

Test the most important requirement explicitly:

**Running discover, collect, analyze, rank, or inspect must not download complete repository source code.**

Add automated tests that verify this behavior.

Also test that optional full downloads occur only after explicit user intent.

---

# PART 18 — FINAL QUALITY ASSURANCE AND DELIVERY

Before declaring the project complete:

1. Run all tests.
2. Fix all failures.
3. Run Ruff.
4. Run type checks.
5. Test all CLI commands.
6. Test metadata collection against GitHub using a controlled live test.
7. Verify that no source code is downloaded by default.
8. Verify duplicate detection.
9. Verify storage reporting.
10. Verify README retrieval limits.
11. Verify API rate-limit handling.
12. Verify configuration security.
13. Verify that optional downloads require explicit intent.
14. Update installation documentation.
15. Create a complete README.

Provide installation instructions for:

- Ubuntu and Debian.
- Kali Linux.
- Arch Linux.
- Windows.
- macOS.

Include:

- Prerequisites.
- Python environment setup.
- Installation.
- GitHub token configuration.
- First discovery.
- Metadata collection.
- Repository inspection.
- Research library usage.
- Optional downloads.
- Troubleshooting.

---

# FINAL PRODUCT REQUIREMENT

RepoHunter must follow this philosophy:

**DISCOVER THOUSANDS. UNDERSTAND HUNDREDS. DOWNLOAD ONLY WHAT MATTERS.**

The default workflow is:

GitHub Discovery
→ Metadata Collection
→ Repository Classification
→ Quality Evaluation
→ Optional AI Analysis
→ Local Research Library
→ Search, Compare and Report

Full repository downloading is a separate, optional operation.

Build this as a reliable, efficient, professional terminal application that can manage thousands of repository records without requiring thousands of local source-code downloads.

Do not stop after creating files or generating code. Implement the application, run the tests, fix the errors, and demonstrate working CLI commands with realistic output.

At completion, provide:

- Implemented features.
- Project architecture.
- Commands available.
- Tests executed and results.
- Known limitations.
- Installation instructions.
- Example metadata-only workflow.

**Most important acceptance criterion: RepoHunter must be useful even if the user never downloads a single repository.**