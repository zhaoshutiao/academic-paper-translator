# Academic Paper Translator

一款给留子、研究生、社科阅读周、文献综述季准备的论文全文翻译 Skill。

之前在海外留学的时候常常要面临一门课一周5篇超长paper，每篇几十页，全英文，句子长、术语密、引用多，不读还不行因为教授特别喜欢在seminar 里点人起来讨论（小学点名起来背课文的恐惧为何追杀我到现在）。学术论文读起来本来就费脑，更别说还要是用外语，好多时候分不清到底是花在查单词的时间上更多还是理解论文的时间更多。最开始逞强的想法是死磕全英论文，但是后来在ddl的追杀前绝望的承认进度太紧不吃不喝一个月大概能坚持完全看懂这几篇paper。这个时候就会特别想念母语环境，虽然中文论文不影响内容的难度，但是扫一眼就能捕捉到关键点的阅读效率实在是比英文阅读要好太多。

总之，不认真读觉得对不起自己的学费，认真读完又觉得脑子疼。

后来感谢天感谢地感谢Open AI，有了GPT的辅助确实轻松了很多。但长文翻译还是有一些很烦人的问题：文章一长，它可能翻着翻着就开始漏段，或者把几页内容压成一小段总结；页码、引用、图表编号这些细节也容易丢；有时候同一个术语前后翻得不一样，读起来很割裂。这个时候就需要我手动把文章切分成不同的段落，一块一块的喂给AI。体验确实比古法查单词快多了，但整个过程还是很机械、很重复，也很不自动化。

所以我做了这个 Skill，让AI来实现切块-翻译-合并-输出完整的中文翻译。而你需要做的，只是把英文论文文档丢进去，然后拿到一份可以通读、可以对照、可以继续精读的中文版本。


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

这个仓库的 Skill 本体在 `skill/academic-paper-translator/`。把这个目录安装到 skills 目录后，对你的AI Agent说说：

```text
Use $academic-paper-translator to translate this long English academic paper into a complete Chinese full-text translation.
```

或者直接说：

```text
使用academic-paper-translator帮我把这篇英文论文完整翻译成中文，不要摘要，保留页码、引用、公式、图表编号和参考文献。
```


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


## 可能存在的问题

这个 Skill 的目标是让长论文翻译更稳定、更可检查，但它不会神奇修复所有问题：

- 扫描版 PDF 可能需要 OCR。
- 双栏 PDF 可能出现文本顺序错乱。
- 复杂表格可能需要人工整理。
- 图像里的文字不一定能提取。
- 翻译质量仍然需要人工抽查，尤其是理论概念、统计结果和关键论证。

最保险的使用方式是：先让 Skill 生成完整中文全文，再带着中文理解回到英文原文精读重点段落。它负责帮你拆掉语言门槛，你负责做最后的判断。


```

- `README.md`：GitHub 首页介绍。
- `skill/academic-paper-translator/SKILL.md`：Codex 使用这个 Skill 时读取的核心工作流。
- `skill/academic-paper-translator/references/translation_style.md`：中文学术翻译风格规则。
- `skill/academic-paper-translator/references/content_type_rules.md`：公式、图表、引用、参考文献等内容类型处理规则。
- `skill/academic-paper-translator/scripts/extract_source.py`：从论文文件提取文本。
- `skill/academic-paper-translator/scripts/chunk_paper.py`：把长论文切成可翻译 chunk。
- `skill/academic-paper-translator/scripts/check_manifest.py`：检查翻译进度。
- `skill/academic-paper-translator/scripts/qa_translation.py`：检查结构性漏翻和标记丢失。
- `skill/academic-paper-translator/scripts/merge_translations.py`：合并最终译文。
