## 1. 回归覆盖

- [x] 1.1 增加一个失败的 DOCX 抽取测试，覆盖“章节开头的 figure 引用句 + 紧随其后的独立 `Figure 5` caption”场景。
- [x] 1.2 在该回归测试中同时覆盖 `extract_docx_book` 和 `extract_docx_chapter_by_anchors`。

## 2. 抽取修复

- [x] 2.1 收紧 `scripts/docx_parity/extract_docx.py` 中的合成 spillover-caption 判定，确保只有在存在真实 spillover 证据时才把混合正文转换成 caption。
- [x] 2.2 保持现有测试夹具所依赖的独立 caption 与 pre-heading spillover 行为不变。

## 3. 校验

- [x] 3.1 运行定向 `tests/docx_parity/test_extract_docx.py`，覆盖新增回归和相邻的 spillover 场景。
- [x] 3.2 运行英文第 5 章的窄范围 DOCX parity 校验，确认 figure 引导句被保留下来。
