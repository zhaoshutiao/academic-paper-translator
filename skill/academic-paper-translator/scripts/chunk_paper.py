#!/usr/bin/env python3
"""Chunk extracted paper Markdown and create a translation manifest."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


PAGE_RE = re.compile(r"^\[Page\s+(\d+)\]\s*$", re.IGNORECASE)
MARKDOWN_HEADING_RE = re.compile(r"^#{1,6}\s+\S.+$")
NUMBERED_HEADING_RE = re.compile(r"^\d+(?:\.\d+)*\.?\s+[A-Z][A-Za-z0-9 ,:;()/-]{1,80}$")
REFERENCES_RE = re.compile(r"^(#{1,6}\s*)?(references|bibliography|works cited)\s*$", re.IGNORECASE)
COMMON_HEADING_RE = re.compile(
    r"^(abstract|keywords?|introduction|background|related work|methods?|methodology|experiments?|results|discussion|conclusion|appendix)\s*$",
    re.IGNORECASE,
)


def split_blocks(text: str) -> list[str]:
    raw_blocks = re.split(r"\n\s*\n", text.replace("\r\n", "\n"))
    return [block.strip() for block in raw_blocks if block.strip()]


def classify(block: str, in_references: bool) -> str:
    if PAGE_RE.match(block):
        return "page_marker"
    if REFERENCES_RE.match(block):
        return "references_heading"
    if in_references:
        return "reference_list"
    if re.match(r"^(figure|fig\.)\s*\d+", block, re.IGNORECASE):
        return "figure_caption"
    if re.match(r"^table\s*\d+", block, re.IGNORECASE):
        return "table_caption"
    if block.startswith("$$") or re.search(r"\\begin\{equation|\\\[|\\\(|^\s*[A-Za-z]\s*=", block):
        return "formula"
    if MARKDOWN_HEADING_RE.match(block):
        return "heading"
    if NUMBERED_HEADING_RE.match(block) and len(block.split()) <= 12:
        return "heading"
    if COMMON_HEADING_RE.match(block):
        return "heading"
    return "body"


def safe_slug(text: str, fallback: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return (slug[:50].strip("-") or fallback).lower()


def write_chunk(out_dir: Path, chunk: dict, blocks: list[str]) -> None:
    chunk_path = out_dir / "chunks" / f"{chunk['id']}.md"
    header = [
        f"<!-- chunk_id: {chunk['id']} -->",
        f"<!-- section: {chunk['section']} -->",
        f"<!-- page: {chunk.get('page') or ''} -->",
        f"<!-- type: {chunk['type']} -->",
        "",
    ]
    chunk_path.write_text("\n".join(header + blocks).strip() + "\n", encoding="utf-8")


def build_chunks(source_text: str, max_chars: int) -> tuple[list[dict], list[list[str]]]:
    blocks = split_blocks(source_text)
    chunks: list[dict] = []
    chunk_blocks: list[list[str]] = []
    current_blocks: list[str] = []
    current_chars = 0
    current_section = "front-matter"
    current_page: str | None = None
    chunk_start_page: str | None = None
    chunk_pages: list[str] = []
    in_references = False

    def flush(chunk_type: str = "body") -> None:
        nonlocal current_blocks, current_chars, chunk_start_page, chunk_pages
        if not current_blocks:
            return
        chunk_number = len(chunks) + 1
        section_slug = safe_slug(current_section, "section")
        chunk_id = f"{chunk_number:04d}_{section_slug}"
        pages = chunk_pages[:]
        if chunk_start_page and chunk_start_page not in pages:
            pages.insert(0, chunk_start_page)
        chunk = {
            "id": chunk_id,
            "section": current_section,
            "page": pages[0] if pages else None,
            "page_start": pages[0] if pages else None,
            "page_end": pages[-1] if pages else None,
            "pages": pages,
            "type": chunk_type,
            "status": "pending",
            "characters": current_chars,
        }
        chunks.append(chunk)
        chunk_blocks.append(current_blocks)
        current_blocks = []
        current_chars = 0
        chunk_start_page = None
        chunk_pages = []

    for block in blocks:
        if PAGE_RE.match(block):
            current_page = PAGE_RE.match(block).group(1)  # type: ignore[union-attr]
            if current_blocks and current_chars + len(block) > max_chars:
                flush()
            if current_page not in chunk_pages:
                chunk_pages.append(current_page)
            current_blocks.append(block)
            current_chars += len(block)
            continue

        block_type = classify(block, in_references)
        if chunk_start_page is None:
            chunk_start_page = current_page
        if block_type == "references_heading":
            flush()
            in_references = True
            current_section = "References"
            chunk_start_page = current_page
            current_blocks.append(block)
            current_chars = len(block)
            continue

        if block_type == "heading" and not in_references:
            if current_blocks:
                flush()
            current_section = re.sub(r"^#{1,6}\s+", "", block).strip()
            chunk_start_page = current_page
            current_blocks.append(block)
            current_chars = len(block)
            continue

        projected = current_chars + len(block) + 2
        if current_blocks and projected > max_chars and block_type not in {"formula", "figure_caption", "table_caption"}:
            flush("reference_list" if in_references else "body")
            chunk_start_page = current_page

        current_blocks.append(block)
        current_chars += len(block) + 2

    flush("reference_list" if in_references else "body")
    return chunks, chunk_blocks


def main() -> None:
    parser = argparse.ArgumentParser(description="Chunk extracted paper source.")
    parser.add_argument("source", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--max-chars", type=int, default=6000)
    args = parser.parse_args()

    text = args.source.read_text(encoding="utf-8")
    chunks, blocks_by_chunk = build_chunks(text, args.max_chars)

    (args.out / "chunks").mkdir(parents=True, exist_ok=True)
    (args.out / "translations").mkdir(parents=True, exist_ok=True)
    (args.out / "final").mkdir(parents=True, exist_ok=True)

    for chunk, blocks in zip(chunks, blocks_by_chunk):
        write_chunk(args.out, chunk, blocks)

    manifest = {
        "source": str(args.source),
        "max_chars": args.max_chars,
        "chunk_count": len(chunks),
        "chunks": chunks,
    }
    progress = {
        "total": len(chunks),
        "translated": 0,
        "missing": [chunk["id"] for chunk in chunks],
    }

    (args.out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.out / "progress.json").write_text(json.dumps(progress, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    glossary = args.out / "glossary.json"
    if not glossary.exists():
        glossary.write_text("{}\n", encoding="utf-8")

    print(f"Wrote {len(chunks)} chunks to {args.out / 'chunks'}")


if __name__ == "__main__":
    main()
