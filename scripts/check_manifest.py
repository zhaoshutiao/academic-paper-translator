#!/usr/bin/env python3
"""Check which manifest chunks have translation files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from json import JSONDecodeError


def main() -> None:
    parser = argparse.ArgumentParser(description="Check paper translation progress.")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--translations", type=Path, required=True)
    parser.add_argument("--write-progress", type=Path)
    args = parser.parse_args()

    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"Manifest not found: {args.manifest}")
        raise SystemExit(2)
    except JSONDecodeError as exc:
        print(f"Manifest is not valid JSON: {args.manifest} ({exc})")
        raise SystemExit(2)
    translated: list[str] = []
    missing: list[str] = []

    for chunk in manifest["chunks"]:
        path = args.translations / f"{chunk['id']}.md"
        if path.exists() and path.read_text(encoding="utf-8").strip():
            translated.append(chunk["id"])
            chunk["status"] = "translated"
        else:
            missing.append(chunk["id"])
            chunk["status"] = "pending"

    progress = {
        "total": len(manifest["chunks"]),
        "translated": len(translated),
        "missing_count": len(missing),
        "missing": missing,
    }

    if args.write_progress:
        args.write_progress.write_text(json.dumps(progress, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(progress, ensure_ascii=False, indent=2))
    raise SystemExit(0 if not missing else 1)


if __name__ == "__main__":
    main()
