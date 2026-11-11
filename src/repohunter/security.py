from __future__ import annotations

import re
from pathlib import Path
from typing import Any

SEVERITY_ORDER = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "INFO": 0}


def redact_sensitive_text(value: str) -> str:
    redacted = re.sub(r"(AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})", "[REDACTED]", value)
    redacted = re.sub(r"(aws[_-]?secret[_-]?access[_-]?key\s*[:=]\s*)([^\s\"']+)", r"\1[REDACTED]", redacted, flags=re.IGNORECASE)
    return redacted


def summarize_findings(findings: list[dict[str, Any]]) -> dict[str, int]:
    summary = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
    for finding in findings:
        severity = str(finding.get("severity", "INFO")).upper()
        if severity in summary:
            summary[severity] += 1
    return summary


def scan_repository(path: str | Path) -> list[dict[str, Any]]:
    root = Path(path)
    findings: list[dict[str, Any]] = []
    if not root.exists():
        return findings
    patterns = {
        "CRITICAL": [
            re.compile(
                r"(AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})"
            ),
            re.compile(
                r"(aws[_-]?secret[_-]?access[_-]?key|password\s*[:=]\s*[\"']?[A-Za-z0-9_!@#$%^&*()-=+]{6,})",
                re.IGNORECASE,
            ),
        ],
        "HIGH": [
            re.compile(
                r"(api[_-]?key|token|secret)\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{8,}", re.IGNORECASE
            ),
            re.compile(r"(curl\s+.*\|\s*(bash|sh)|wget\s+.*\|\s*(bash|sh))", re.IGNORECASE),
        ],
        "MEDIUM": [
            re.compile(r"(DROP\s+TABLE|rm\s+-rf|chmod\s+\+x\s+/tmp)", re.IGNORECASE),
            re.compile(r"(eval\(|exec\()", re.IGNORECASE),
        ],
    }

    for file in root.rglob("*"):
        if not file.is_file():
            continue
        if file.suffix.lower() in {
            ".py",
            ".js",
            ".ts",
            ".sh",
            ".bash",
            ".yaml",
            ".yml",
            ".json",
            ".env",
            ".ini",
            ".cfg",
            ".txt",
            ".md",
        }:
            try:
                text = file.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            safe_text = redact_sensitive_text(text)
            for severity, regexes in patterns.items():
                for rx in regexes:
                    if rx.search(safe_text):
                        findings.append(
                            {
                                "severity": severity,
                                "file": str(file.relative_to(root)),
                                "detail": "Pattern matched static security heuristic",
                            }
                        )
    findings.sort(key=lambda item: SEVERITY_ORDER.get(item["severity"], 0), reverse=True)
    return findings
