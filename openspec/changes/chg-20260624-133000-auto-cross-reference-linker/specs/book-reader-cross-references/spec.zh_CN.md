## ADDED Requirements

### Requirement: Reader body copy auto-links supported textual references
`/book/` reader MUST 在 reader enhancement 层完成相关页内锚点创建之后，自动把受支持的正文文本引用转换成链接。

#### Scenario: Figure and table references link to local anchors
- **WHEN** 正文段落中出现 `Figure N` 或 `Table N`
- **AND** 当前页面存在对应的 `#figure-n` 或 `#table-n` 锚点目标
- **THEN** 该文本引用会被转换成指向本页锚点的链接

#### Scenario: Section references link to the current chapter heading
- **WHEN** 正文段落中出现 `Section X.Y`
- **AND** 当前页面存在展示编号以 `X.Y` 开头的 heading
- **THEN** 该文本引用会被转换成指向该 heading 锚点的链接

#### Scenario: Chapter references link to published chapter routes
- **WHEN** 正文段落中出现 `Chapter N`
- **AND** reader 侧栏中存在 `Chapter N` 对应的已发布章节路由
- **THEN** 该文本引用会被转换成指向对应章节页面的链接

#### Scenario: Equation references link to numbered formula anchors
- **WHEN** 正文段落中出现 `Equation X.Y` 或 `Formula X.Y`
- **AND** 当前页面或章节号前缀为 `X` 的已发布章节路由可提供对应的 `#formula-x-y` 目标契约
- **THEN** 该文本引用会被转换成指向该编号公式锚点的链接

### Requirement: Auto-linking must avoid broken or duplicate links
`/book/` reader MUST 对无目标引用保持纯文本，并且 MUST NOT 对已经处于链接内部或已生成的 figure/table/formula 卡片 chrome 内部的引用再次包裹链接。

#### Scenario: Missing target stays plain text
- **WHEN** 一个正文引用无法解析到 figure、table、section 或 chapter 目标
- **THEN** reader 保持原始文本不变

#### Scenario: Existing linked or generated-card content is skipped
- **WHEN** 一个引用出现在现有 `<a>` 元素内部，或者出现在已生成的 figure、table、formula 卡片标记内部
- **THEN** reader 不会再次包裹该引用
