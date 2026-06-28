## Context

英文 reference PDF 与 Chapter 5 的原始 DOCX 内容都包含这样一段结构：Figure 5 之前先有一句正文引导句，后面紧跟一个独立的 figure caption 段落。当前 DOCX 语义抽取器会把任何在首个 outline 之前出现、且包含 `Figure N:` 的段落都当成 caption spillover，即使这段其实是普通正文，且后面已经有一个独立 caption。这个误判会继续传导到替换后的 Markdown、站点渲染结果以及基于 parity 的重建流程。

## Goals / Non-Goals

**Goals:**
- 当引用 figure 的正文段落后面紧跟独立 caption 段落时，将该正文保留为普通 body text。
- 保持当前对真正“粘连/重复式 spillover caption”场景的归一化能力。
- 增加一个同时覆盖 `extract_docx_book` 与 `extract_docx_chapter_by_anchors` 的回归测试。

**Non-Goals:**
- 不在这次变更中重建整个英文版产物。
- 不重做整个 DOCX figure 抽取流水线。
- 不改变独立 `Figure N ...` caption 段落的识别方式。

## Decisions

### Decision: 只有在存在真实 spillover 证据时才从混合段落中合成 caption
最小修复方式是：不要再把所有“首个 outline 之前、恰好包含 caption 子串”的段落都当成合成 caption。现有抽取器已经有 `_is_spillover_caption(...)`，它会通过检查 caption 标记是否在同一段里被粘连、重复或嵌入，来区分真实 spillover 和普通正文。直接复用这个信号，比继续扩大启发式规则更稳妥。

备选方案：
- 对以 `The` 开头或包含逗号的句子做特判。否决，因为这会把英语写作习惯硬编码进规则，对后续内容非常脆弱。

### Decision: 用一个回归测试同时覆盖整书抽取和 anchor 抽取
出问题的启发式逻辑在 `extract_docx_book` 和 `extract_docx_chapter_by_anchors` 中各有一份。回归测试必须同时覆盖两条路径，否则将来只修一边时，parity 专用流程仍可能悄悄回归。

备选方案：
- 只测试 `extract_docx_book`。否决，因为用户可见的 parity 工作流同样依赖 anchor 抽取。

## Risks / Trade-offs

- [某些首个 outline 之前的真实 spillover 段落如果缺少“粘连证据”] → 抽取器可能不再把它归一化成 caption。缓解：保留独立 caption 处理逻辑不变，并继续依赖现有显式 spillover 测试。
- [两个抽取函数中的重复逻辑再次漂移] → 将来可能只回归其中一条路径。缓解：用一个回归测试断言两条路径都输出相同的“正文段落 + caption”结构。

## Migration Plan

1. 先增加一个失败的 DOCX 抽取回归测试，覆盖“章节开头的 figure 引用句 + 紧随其后的独立 caption”场景。
2. 收紧两条抽取路径中的 spillover-caption 判定条件。
3. 运行定向抽取测试和第 5 章的窄范围 parity 校验。
4. 如需回滚，恢复旧的 spillover 条件并删除这条回归测试。

## Open Questions

- None.
