## ADDED Requirements

### Requirement: Front matter MUST expose a numbered equation index
每个 edition 的 web book front matter 都 MUST 发布一个专门的 `List of Equations` 页面。该页面 MUST 紧跟在 `List of Tables` 之后，并且 MUST 只列出那些已经参与 reader equation-navigation 约定的已编号公式。

#### Scenario: English front matter inserts the equation index after tables
- **WHEN** 构建英文 summary 与站点
- **THEN** `chapters/list-of-equations.html` 存在，且顺序位于 `chapters/list-of-tables.html` 之后

#### Scenario: French front matter inserts the equation index after tables
- **WHEN** 构建法文 summary 与站点
- **THEN** `chapters/list-of-equations.html` 存在，且顺序位于 `chapters/list-of-tables.html` 之后

### Requirement: Equation index links MUST reuse stable numbered formula anchors
公式索引页 MUST 复用从 `data-equation-label` 生成的现有 numbered formula anchors，这样每个已编号公式只会有一个 canonical 导航目标。

#### Scenario: Numbered equation links target formula anchors
- **WHEN** 某个公式出现在索引页中
- **THEN** 它的链接指向所属章节中的现有 `#formula-<number>` 锚点

#### Scenario: Unnumbered formulas stay out of the equation index
- **WHEN** 某个公式块没有 numbered equation label
- **THEN** 它不会被收录进 `List of Equations`
