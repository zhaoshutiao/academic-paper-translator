#!/usr/bin/env python3
"""Merge chunk translations into a final full-text Markdown file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge translated paper chunks.")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--translations", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    missing: list[str] = []
    parts: list[str] = []

    for chunk in manifest["chunks"]:
        path = args.translations / f"{chunk['id']}.md"
        if not path.exists() or not path.read_text(encoding="utf-8").strip():
            missing.append(chunk["id"])
            continue
        parts.append(path.read_text(encoding="utf-8").strip())

    if missing:
        print("Missing translations:")
        for chunk_id in missing:
            print(f"- {chunk_id}")
        raise SystemExit(1)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n\n".join(parts).strip() + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()

