# Book SearchBox Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `/book/` 搜索重建为主题层自有的工具栏 `SearchBox`，使用本地 mdBook 索引数据，并对齐已确认的聚焦式下拉交互模型。

**Architecture:** 保留 `searchindex.js` 作为数据源，停止加载 mdBook `searcher.js`，把所有搜索状态、过滤、渲染和关闭行为迁移到 `theme/custom.js`。在 `theme/index.hbs` 和 `theme/custom.css` 中做小范围改动，为清空按钮、状态驱动的宽度变化和绝对定位下拉层提供支撑，然后通过 `npm run test:site` 验证。

**Tech Stack:** mdBook、Handlebars、vanilla JavaScript、CSS、基于 shell 的渲染断言

---

**File Map**

- `theme/index.hbs`：负责书籍主题中的搜索标记和脚本引入。
- `theme/custom.js`：负责 `SearchBox` 控制器、懒加载索引、过滤、渲染、关闭、键盘行为和高亮传递。
- `theme/custom.css`：负责搜索外壳宽度状态样式与下拉/结果展示。
- `scripts/test-site-render.sh`：负责主题源码和生成后的 `/public/book` 输出回归断言。

### Task 1: Update Search Markup And Assertions

**Files:**
- Modify: `theme/index.hbs`
- Modify: `scripts/test-site-render.sh`

- [ ] **Step 1: Replace the default mdBook search hook points in the template**

更新 `theme/index.hbs` 中的搜索块，保留现有 id，但加入 clear 按钮，并停止加载 `searcher.js`。

- [ ] **Step 2: Assert the new template markers and script contract**

更新 `scripts/test-site-render.sh`，检查 clear 按钮、聚焦式下拉绑定标记，以及模板源码中不再包含 `searcher.js`。

- [ ] **Step 3: Run the render test to confirm the new assertions fail before implementation is complete**

Run: `npm run test:site`

Expected: 在 JS/CSS 实现完整落地前，新增的搜索标记或脚本断言先失败。

### Task 2: Implement The SearchBox Controller

**Files:**
- Modify: `theme/custom.js`
- Test: `scripts/test-site-render.sh`

- [ ] **Step 1: Add a theme-owned search state controller**

实现本地 `query`、`focused`、`results` 和 `activeIndex` 状态；懒加载 `searchindex.js`；按 `title`、`body` 和 `breadcrumbs` 过滤；渲染下拉层和空态。

- [ ] **Step 2: Add interaction handling**

实现进入聚焦、外部点击 `mousedown` 关闭、clear 按钮 `mousedown` 阻止失焦、清空/重置、结果跳转、`/` 和 `s` 快捷键，以及可选的 Arrow/Enter/Escape 键盘行为。

- [ ] **Step 3: Preserve highlight-on-navigation behavior**

给结果链接附加 `highlight=<query>`，并在目标页加载时若存在该参数则用 `Mark` 高亮正文。

### Task 3: Add CSS Support And Verify

**Files:**
- Modify: `theme/custom.css`
- Test: `scripts/test-site-render.sh`

- [ ] **Step 1: Add focused-width and dropdown styles**

为工具栏搜索槽位增加样式：通过 JS 控制的聚焦类让输入框略微变宽，clear 按钮位于输入框内部，结果面板以下拉层形式绝对定位在输入框下方。

- [ ] **Step 2: Style result rows and empty state just enough to support the interaction**

为结果行、激活结果状态、图标标签、摘录和空态容器添加必要选择器，但不重做更大范围的阅读器外壳设计。

- [ ] **Step 3: Run the full site render assertions**

Run: `npm run test:site`

Expected: PASS.
