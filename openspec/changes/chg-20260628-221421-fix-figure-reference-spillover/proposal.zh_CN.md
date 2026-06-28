## Why

第 5 章当前与已发布 PDF 不一致，因为 DOCX 抽取流程把 Figure 5 前面的引导句误判成了图注 spillover。这会丢掉图前的说明句，并让章节 Markdown 与站点渲染结果只剩下一段被截断的 caption 碎片，而不是原本应有的“正文引导句 + 独立图注”结构。

## What Changes

- 收紧 DOCX 图注 spillover 的判定规则，确保只是引用图号的正文句子会被保留为普通段落，而不是被截断成 caption。
- 增加一个回归测试，覆盖“章节开头的 figure 引导句 + 紧随其后的独立 figure caption”场景。
- 通过修正后的抽取行为间接恢复第 5 章的 Markdown 语义输出，确保后续 parity 与重建流程持续保留正确文本结构。

## Capabilities

### New Capabilities
- `docx-figure-reference-preservation`：DOCX 语义抽取在真正图注之前，必须保留引用 figure 的正文段落句子，而不能把它截断并并入 caption。

### Modified Capabilities
- None.

## Impact

- 受影响源码：`scripts/docx_parity/extract_docx.py`、`tests/docx_parity/test_extract_docx.py`
- 受影响生成语义：第 5 章 Figure 5 引导句抽取结果及其下游 Markdown parity 输出
- 校验面：定向 DOCX 抽取测试与第 5 章 DOCX parity 检查
- 不引入新的运行时依赖
