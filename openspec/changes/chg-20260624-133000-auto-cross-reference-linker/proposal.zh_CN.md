## Why

当前 `/book/` reader 已经会为图、表和编号公式生成稳定锚点，但正文里的 `Figure 79`、`Table 17`、`Section 8.5`、`Chapter 12` 这类引用仍然只是纯文本。这样既让 reader 里的高价值导航失效，也会把维护工作推回到逐条手工改章节 Markdown。

## What Changes

- 在 `theme/custom.js` 中新增运行时正文交叉引用链接器。
- 复用现有 reader 锚点契约，把 `Figure N` 自动链接到 `#figure-n`，把 `Table N` 自动链接到 `#table-n`。
- 基于 mdBook 已输出的当前章节 heading ID 解析 `Section X.Y`。
- 基于 reader 左侧边栏里已发布的章节路由解析 `Chapter N`。
- 基于现有编号公式锚点解析 `Equation X.Y` 与 `Formula X.Y`，优先链接当前页，若编号前缀对应其他已发布章节则链接到对应章节页内公式锚点。
- 对找不到目标的引用保持纯文本，不生成坏链接。

## Capabilities

### New Capabilities
- `book-reader-cross-references`：`/book/` reader 能自动把正文中的高价值文本引用链接到正确的书内锚点或章节页面，而不需要手工补 Markdown 链接；当存在稳定编号公式标签时，也会自动链接公式引用。

### Modified Capabilities
- None.

## Impact

- 受影响源码：`theme/custom.js`、`scripts/test-site-render.sh`、`tests/test_theme_custom_css.py`
- 受运行时增强影响的页面：`/book/chapters/*.html`
- 不引入新的运行时依赖
- 该引用链接行为本身不需要直接修改已发布章节 Markdown
