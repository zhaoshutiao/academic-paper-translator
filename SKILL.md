---
name: academic-paper-translator
description: Use this skill to translate long English academic papers into complete Chinese full-text translations when the document is too long for one response. Supports PDF, DOCX, Markdown, LaTeX, TXT, and similar paper sources by extracting text, chunking by structure, preserving page markers, figures, tables, formulas, citations, and untranslated references, then translating chunk by chunk with glossary consistency, checkpointing, QA, and final assembly.
---

# Academic Paper Translator

## Purpose

Translate long English academic papers into complete Chinese full-text translations. The output should be clear, easy to understand, and academically professional while preserving the paper's structure, page markers, figure/table numbers, formulas, citation markers, and original reference list.

This skill is designed for long documents. Do not attempt to translate the whole paper in one chat response. Always create chunk files, translation files, progress state, and a final assembled output.

## Default Output

- Produce a Chinese-only full translation.
- Prefer Markdown for the final deliverable unless the user asks for another format.
- Preserve page markers as `[Page N]` when available.
- Preserve formulas, equation numbers, variable names, DOIs, URLs, citation markers, figure/table numbers, and reference entries.
- Translate figure/table captions and footnotes, but keep their numbering.
- Do not translate reference entries. The References/Bibliography heading may be translated as `参考文献`, but the entries themselves must remain unchanged.

For style rules, read `references/translation_style.md` before translating. For content-type handling, read `references/content_type_rules.md` before processing figures, formulas, tables, citations, pages, or references.

## Workflow

### 1. Create a Workspace

Create a task directory under the current workspace, for example:

```text
work/paper_translation/
  source/
  chunks/
  translations/
  final/
  manifest.json
  glossary.json
  progress.json
```

If resuming an existing translation, inspect `manifest.json`, `progress.json`, and `translations/` first. Continue only missing or failed chunks.

### 2. Extract Source Text

Use `scripts/extract_source.py` from the skill directory, or use the script's absolute path:

```bash
python scripts/extract_source.py /path/to/paper.pdf --out work/paper_translation/source
```

The script writes:

- `source.md`: extracted text with page markers when available
- `source_metadata.json`: source format and extraction notes

If extraction loses important structure, manually repair headings, page markers, formulas, or captions in `source.md` before chunking.

### 3. Chunk the Paper

Use `scripts/chunk_paper.py` from the skill directory, or use the script's absolute path:

```bash
python scripts/chunk_paper.py work/paper_translation/source/source.md --out work/paper_translation --max-chars 6000
```

The script writes:

- `manifest.json`
- `chunks/*.md`
- `progress.json`

Chunks should preserve semantic boundaries where possible. Avoid splitting a formula, figure caption, table caption, or reference entry. Inspect `manifest.json` after chunking; if a normal sentence was treated as a section title or page ranges look wrong, repair `source.md` or adjust the chunks before translating.

### 4. Build a Glossary

Before translating all chunks, inspect the title, abstract, keywords, and introduction chunks. Create `glossary.json` with important terms:

```json
{
  "large language model": "大语言模型",
  "retrieval-augmented generation": "检索增强生成",
  "ablation study": "消融实验"
}
```

Update the glossary when new recurring technical terms appear. Keep translations consistent across chunks.

### 5. Translate Chunk by Chunk

For each pending chunk:

1. Read `references/translation_style.md`, `references/content_type_rules.md`, `glossary.json`, and the chunk file.
2. Translate the chunk into Chinese according to the style and content rules.
3. Save the translation to `translations/<chunk_id>.md`.
4. Keep the same chunk id and preserve page markers.
5. Run QA for that chunk before moving on.

When translating:

- Translate the full content of the chunk. Do not summarize.
- Preserve Markdown heading structure where possible.
- Keep formulas and equation blocks unchanged.
- Keep citation markers unchanged, including `[1]`, `[2, 5]`, `(Smith, 2020)`, and `Smith et al. (2020)`.
- Keep reference entries in English, unchanged. The heading may be translated as `参考文献`.
- If the source chunk contains ambiguous terminology, choose a consistent academic translation and add it to `glossary.json`.

### 6. Check Progress

Use `scripts/check_manifest.py` from the skill directory, or use the script's absolute path:

```bash
python scripts/check_manifest.py work/paper_translation/manifest.json --translations work/paper_translation/translations --write-progress work/paper_translation/progress.json
```

Only proceed to final assembly when all non-skipped chunks are translated.

### 7. Run QA

Use `scripts/qa_translation.py` from the skill directory, or use the script's absolute path:

```bash
python scripts/qa_translation.py work/paper_translation/manifest.json --translations work/paper_translation/translations
```

By default, the QA script exits non-zero for medium or high severity issues. Address reported issues before final assembly when they indicate missing page markers, formulas, citations, figure/table numbers, changed references, or untranslated body chunks. Use `--fail-on high`, `--fail-on low`, or `--fail-on none` only when you intentionally want a different threshold.

### 8. Merge Final Translation

Use `scripts/merge_translations.py` from the skill directory, or use the script's absolute path:

```bash
python scripts/merge_translations.py work/paper_translation/manifest.json --translations work/paper_translation/translations --out work/paper_translation/final/paper_zh.md
```

After merging, inspect the beginning, middle, end, and References section. Confirm the final file is a complete Chinese full-text translation and that reference entries remain in the original language.

## Completion Criteria

The task is complete only when:

- Every chunk in `manifest.json` is translated or intentionally copied unchanged according to its content type.
- `check_manifest.py` reports no missing translation files.
- `qa_translation.py` reports no unresolved medium or high severity structural issues under the default threshold.
- The final Markdown file exists and is ordered according to the original paper.
- The final response to the user includes the final file path and any remaining caveats, such as poor PDF extraction or unrecoverable layout loss.
