# Academic Paper Translator

一款给留子、研究生、社科阅读周、文献综述季准备的论文全文翻译 Skill。

如果你也经历过那种课表：一门课一周 5 篇 paper，每篇几十页，全英文，句子长、术语密、引用多，教授还特别爱在 seminar 里追问细节。读论文本来就费脑，更别说还要隔几行查一次词。眼睛扫中文时可以瞬间抓关键词，扫英文 paper 时却常常要先解码句法，再理解论证，最后还得记住作者到底在反驳谁。

LLM 出现之后确实救命，但长论文翻译还有几个老问题：

- 翻到七八页以后开始漏段、跳段，甚至悄悄把中间内容总结掉。
- 引用、页码、公式、表格编号容易丢，回头想对照原文很痛苦。
- 参考文献可能被错误翻译或改写。
- 术语前后不一致，同一个概念前面一个译法、后面又换一个译法。
- 论文越长，越容易变成“看起来完整，实际上缺了一块”的译文。
- 遇到需要逐字较真的 professor，普通 AI 辅助很难让人放心。

所以我做了这个 Skill：把一篇很长的英文论文拆成可控的小块，逐块翻译、逐块检查，最后再合并成完整中文全文。它不是只给你一个摘要，也不是翻到一半就开始偷懒，而是围绕“完整读完一篇 paper”这个场景设计的。

## 它适合谁

- 海外社科、人文、教育、心理、管理、传播等专业学生
- 每周需要读大量英文 paper 的留学生
- 正在写 literature review、reading response、seminar notes 的人
- 想先用中文通读全文，再回到英文原文精读的人
- 需要保留页码、引用、图表编号，方便课堂讨论和写作引用的人

## 支持格式

当前支持：

- PDF
- DOCX
- Markdown
- LaTeX / TeX
- TXT

对 PDF 的支持是 best-effort：如果原 PDF 是双栏、扫描版、公式很多、表格很复杂，抽取效果可能受原文件质量影响。Skill 会尽量保留页码、公式、图表标题、引用和参考文献，但复杂论文仍建议先检查提取出的 `source.md`。

## 核心能力

- **长文分块翻译**：不再把几十页论文一次性塞进模型，降低漏翻风险。
- **完整全文输出**：目标是生成可通读的中文全文，而不是摘要。
- **页码保留**：尽量保留 `[Page N]`，方便回查原文。
- **引用保护**：保留 `[1]`、`[2, 5]`、`(Smith, 2020)` 等引用标记。
- **公式保护**：公式、变量名、 equation number 尽量保持原样。
- **图表编号保护**：保留 `Figure 2`、`Table 1`、`Fig. 3` 等编号。
- **参考文献不翻译**：参考文献条目保持原文，避免 DOI、标题、作者信息被改坏。
- **术语表一致性**：翻译前建立 `glossary.json`，让关键术语前后一致。
- **进度可恢复**：中途停下也可以根据 `manifest.json` 和 `progress.json` 继续。
- **结构 QA 检查**：用脚本检查漏文件、漏页码、漏引用、漏图表编号、漏 DOI、参考文献改动等问题。

## 它怎么工作

这个 Skill 会把论文翻译流程拆成几个步骤：

1. 从 PDF / DOCX / Markdown / LaTeX / TXT 提取文本。
2. 生成带页码和结构信息的 `source.md`。
3. 按章节和长度切成多个 chunk。
4. 先建立术语表，再逐 chunk 翻译。
5. 每个 chunk 翻译后跑 QA。
6. 检查所有 chunk 是否完成。
7. 合并成最终中文 Markdown 全文。

典型输出结构：

```text
work/paper_translation/
  source/
    source.md
    source_metadata.json
  chunks/
  translations/
  final/
    paper_zh.md
  manifest.json
  glossary.json
  progress.json
```

## 怎么使用

把这个仓库作为 Codex Skill 安装或放入你的 Codex skills 目录后，对 Codex 说：

```text
Use $academic-paper-translator to translate this long English academic paper into a complete Chinese full-text translation.
```

或者直接说：

```text
帮我把这篇英文论文完整翻译成中文，不要摘要，保留页码、引用、公式、图表编号和参考文献。
```

Skill 会指导 Codex 使用 `scripts/` 里的工具完成提取、分块、检查和合并。

## 适合翻译哪些论文

它默认适合大多数英文 academic papers，尤其是这些场景：

- 社科理论论文
- empirical research paper
- literature review
- education / psychology / sociology paper
- machine learning / CS paper
- medical / biomedical paper
- economics / management paper
- humanities paper
- thesis chapter 或 long report

不同领域的术语仍然需要你或 Codex 在 `glossary.json` 里逐步维护。越是专业的论文，术语表越重要。

## 这不是魔法

这个 Skill 的目标是让长论文翻译更稳定、更可检查，但它不会神奇修复所有问题：

- 扫描版 PDF 可能需要 OCR。
- 双栏 PDF 可能出现文本顺序错乱。
- 复杂表格可能需要人工整理。
- 图像里的文字不一定能提取。
- 翻译质量仍然需要人工抽查，尤其是理论概念、统计结果和关键论证。

最推荐的使用方式是：先让 Skill 生成完整中文全文，再带着中文理解回到英文原文精读重点段落。它负责帮你拆掉语言门槛，你负责做最后的判断。

## 文件说明

```text
academic-paper-translator/
  SKILL.md
  agents/
    openai.yaml
  references/
    translation_style.md
    content_type_rules.md
  scripts/
    extract_source.py
    chunk_paper.py
    check_manifest.py
    qa_translation.py
    merge_translations.py
```

- `SKILL.md`：Codex 使用这个 Skill 时读取的核心工作流。
- `references/translation_style.md`：中文学术翻译风格规则。
- `references/content_type_rules.md`：公式、图表、引用、参考文献等内容类型处理规则。
- `scripts/extract_source.py`：从论文文件提取文本。
- `scripts/chunk_paper.py`：把长论文切成可翻译 chunk。
- `scripts/check_manifest.py`：检查翻译进度。
- `scripts/qa_translation.py`：检查结构性漏翻和标记丢失。
- `scripts/merge_translations.py`：合并最终译文。

## 一句话总结

这不是“帮我总结一下这篇 paper”的小工具，而是一个为长论文全文翻译设计的自助工作流：能拆、能译、能查、能续、能合并。适合那些真的要读完 paper，而不是只想假装读过的人。
