# Translation Style

Use this style for English academic paper translation into Chinese.

## Tone

- Clear, readable, and academically professional.
- Faithful to the original argument and evidence.
- Prefer natural academic Chinese over rigid word-by-word translation.
- Avoid casual phrasing, marketing tone, and excessive embellishment.
- Do not summarize unless the user explicitly asks for a summary.

## Terminology

- Follow `glossary.json` exactly for recurring technical terms.
- When a new important term appears, choose a stable Chinese translation and add it to the glossary.
- Keep standard English acronyms when commonly used, and provide Chinese meaning nearby when helpful, for example: `检索增强生成（RAG）`.
- Keep model names, dataset names, software names, benchmark names, theorem names, and product names unchanged unless there is a widely accepted Chinese translation.

## Sentence Handling

- Preserve the meaning and logical relationships of the original.
- Split very long English sentences into readable Chinese sentences when needed.
- Preserve hedging and uncertainty, such as `may`, `suggests`, `indicates`, `likely`, and `we hypothesize`.
- Preserve contrast, causality, limitation, and scope markers.

## Academic Conventions

- Translate `we` according to context. In most papers, use `我们`.
- Translate section headings into concise academic Chinese.
- Keep citation markers unchanged.
- Keep equations and variables unchanged.
- Do not add claims, explanations, or interpretations not present in the source.

## Final Output Quality

The final translation should read like a complete Chinese academic manuscript, not a stitched set of disconnected machine-translation fragments. Maintain consistent terminology, tense, and section naming across the document.

