#!/usr/bin/env python3
"""Best-effort structural QA for translated academic paper chunks."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


MARKER_PATTERNS = {
    "page": re.compile(r"\[Page\s+\d+\]", re.IGNORECASE),
    "numeric_citation": re.compile(r"\[[0-9][0-9,\-\s;]*\]"),
    "equation_number": re.compile(r"\([0-9]{1,3}\)"),
    "figure": re.compile(r"\b(?:Figure|Fig\.)\s*\d+[A-Za-z]?", re.IGNORECASE),
    "table": re.compile(r"\bTable\s*\d+[A-Za-z]?", re.IGNORECASE),
    "doi": re.compile(r"\bdoi:\s*\S+|https?://doi\.org/\S+", re.IGNORECASE),
}

REFERENCES_HEADING_RE = re.compile(r"^(#{1,6}\s*)?(references|bibliography|works cited|参考文献)\s*$", re.IGNORECASE)


def find_markers(text: str) -> dict[str, set[str]]:
    return {name: set(pattern.findall(text)) for name, pattern in MARKER_PATTERNS.items()}


def likely_untranslated_body(text: str) -> bool:
    letters = re.findall(r"[A-Za-z]", text)
    cjk = re.findall(r"[\u4e00-\u9fff]", text)
    if len(text) < 200:
        return False
    return len(letters) > max(240, len(cjk) * 2)


def reference_entries(text: str) -> list[str]:
    body = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    entries: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped or REFERENCES_HEADING_RE.match(stripped):
            continue
        entries.append(stripped)
    return entries


def main() -> None:
    parser = argparse.ArgumentParser(description="Run structural QA on chunk translations.")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--translations", type=Path, required=True)
    parser.add_argument("--chunks", type=Path)
    parser.add_argument(
        "--fail-on",
        choices=("high", "medium", "low", "none"),
        default="medium",
        help="Return a non-zero exit code when issues at or above this severity are found.",
    )
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    chunks_dir = args.chunks or args.manifest.parent / "chunks"
    issues: list[dict[str, str]] = []

    for chunk in manifest["chunks"]:
        chunk_id = chunk["id"]
        source_path = chunks_dir / f"{chunk_id}.md"
        translation_path = args.translations / f"{chunk_id}.md"

        if not translation_path.exists() or not translation_path.read_text(encoding="utf-8").strip():
            issues.append({"chunk": chunk_id, "severity": "high", "issue": "missing translation file"})
            continue

        source = source_path.read_text(encoding="utf-8") if source_path.exists() else ""
        translation = translation_path.read_text(encoding="utf-8")

        source_markers = find_markers(source)
        translation_markers = find_markers(translation)
        for marker_type, markers in source_markers.items():
            missing = sorted(markers - translation_markers[marker_type])
            if missing:
                issues.append({
                    "chunk": chunk_id,
                    "severity": "medium",
                    "issue": f"missing {marker_type} marker(s): {', '.join(missing[:8])}",
                })

        if chunk.get("type") != "reference_list" and likely_untranslated_body(translation):
            issues.append({"chunk": chunk_id, "severity": "medium", "issue": "translation may contain a large untranslated English body"})

        if chunk.get("type") == "reference_list":
            source_entries = reference_entries(source)
            translated_entries = reference_entries(translation)
            missing_entries = [entry for entry in source_entries if entry not in translated_entries]
            if missing_entries:
                issues.append({"chunk": chunk_id, "severity": "low", "issue": "reference list may have been changed; references should remain original"})

    report = {
        "issue_count": len(issues),
        "issues": issues,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.fail_on == "none":
        raise SystemExit(0)
    severity_rank = {"low": 1, "medium": 2, "high": 3}
    threshold = severity_rank[args.fail_on]
    should_fail = any(severity_rank[issue["severity"]] >= threshold for issue in issues)
    raise SystemExit(1 if should_fail else 0)


if __name__ == "__main__":
    main()
