# Book Reader Typography And Responsive Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `/book` 阅读器落到已确认的宽屏/窄屏定向设计上，同时把正文排版系统从 “UI 风格标题 serif + 全局 sans” 收敛为“正文与章节标题 serif、界面 chrome sans”。

**Architecture:** 保留 mdBook 作为唯一内容引擎与目录引擎，不改 `src/**/*.md`、`SUMMARY.md`、`book/` 或 `public/book/` 生成产物。实现仅限 `theme/index.hbs`、`theme/custom.css`、必要时的 `theme/custom.js`，并通过 `scripts/test-site-render.sh` 锁定字体导入、正文版式、响应式分页与移动端单列行为。

**Tech Stack:** mdBook, Handlebars theme template, CSS, vanilla JavaScript, shell-based render assertions

---

## Solution Summary

### Confirmed Scope

- 只改布局、样式、最小必要壳层标记，不改正文文本内容。
- 不改章节标题文案、表格数据、术语解释、图表 caption 文案。
- 不引入新的产品功能，不增加 tab、filter、drawer 之外的新交互模型。

### Confirmed Typography

- UI chrome 用 `Inter`：页头、侧栏目录、按钮、搜索、右侧 outline、分页标签、表格表头、术语索引、图表索引。
- 正文系统用 `Literata`，`Georgia` 作为 serif fallback。
- `h1`/`h2`/`h3` 与正文同属 serif 系统，不再使用 sans 标题。
- 宽屏正文目标观感：约 `17px` 到 `18px`，`line-height: 1.68` 左右。
- 窄屏正文目标观感：约 `16px` 到 `16.25px`，`line-height: 1.7` 左右。

### Confirmed Layout

- 宽屏：左侧真实 mdBook sidebar + 中央正文主列 + 右侧安静 outline。
- 中屏：隐藏右侧 outline，保留左侧 sidebar。
- 窄屏/手机：左侧目录仅通过 menu 打开；右侧 outline 隐藏；正文单列；`Previous/Next` 纵向堆叠。

### Confirmed Pagination Behavior

- `>= 761px`：`Previous` 与 `Next` 同一行。
- `<= 760px`：纵向堆叠，全宽卡片。
- 窄屏下两张卡片都左对齐，避免当前“下一章卡片右对齐”带来的阅读跳跃。

### File Map

- `theme/index.hbs`: 只负责字体导入与阅读器壳层结构；允许增加一个轻量的 header center identity，不改 mdBook 内容挂载点。
- `theme/custom.css`: 负责字体系统、正文节奏、表格扫描面板、术语/索引页、响应式断点、分页卡片布局。
- `theme/custom.js`: 默认不改；仅在字体或响应式调整导致 progress / hash scroll / outline 挂载回归时最小修补。
- `scripts/test-site-render.sh`: 锁定字体导入、serif/sans 分工、移动端单列与分页堆叠行为。

### Files To Modify

- `scripts/test-site-render.sh`
- `theme/index.hbs`
- `theme/custom.css`
- `theme/custom.js` only if verification proves it is necessary

---

### Task 1: Lock The New Scope In Render Assertions

**Files:**
- Modify: `scripts/test-site-render.sh`
- Test: `scripts/test-site-render.sh`

- [ ] **Step 1: Replace the old book font assertion and add new typography assertions**

在 `/book` 相关断言区，把旧的 `Inter + Lora` 检查替换为下面这些检查：

```sh
check_contains public/book/index.html 'fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Literata:wght@400;500;600;700&display=swap'
check_not_contains public/book/index.html 'family=Lora'
check_contains theme/custom.css '--reader-sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;'
check_contains theme/custom.css '--reader-serif: "Literata", Georgia, serif;'
check_contains theme/custom.css '.reader-article,'
check_contains theme/custom.css 'font-family: var(--reader-serif);'
check_contains theme/custom.css '.book-toolbar,'
check_contains theme/custom.css '.book-outline-body,'
check_contains theme/custom.css '.reference-index,'
check_contains theme/custom.css '.reference-glossary-list,'
check_contains theme/custom.css '.reader-article table,'
check_contains theme/custom.css 'font-family: var(--reader-sans);'
```

- [ ] **Step 2: Add explicit responsive assertions for the confirmed mobile behavior**

继续在 `/book` 相关断言区加入：

```sh
check_contains theme/custom.css '@media (max-width: 760px) {'
check_contains theme/custom.css '.chapter-pagination {'
check_contains theme/custom.css 'flex-direction: column;'
check_contains theme/custom.css '.chapter-nav-card {'
check_contains theme/custom.css 'width: 100%;'
check_contains theme/custom.css '.chapter-nav-next {'
check_contains theme/custom.css 'text-align: left;'
check_contains theme/custom.css '.reader-article table {'
check_contains theme/custom.css 'display: block;'
check_contains theme/custom.css 'overflow-x: auto;'
```

- [ ] **Step 3: Run the render test to verify the new assertions fail before implementation**

Run:

```bash
npm run test:site
```

Expected: FAIL with a missing pattern such as `family=Literata`, `--reader-serif`, or `text-align: left;`.

- [ ] **Step 4: Commit the red test**

```bash
git add scripts/test-site-render.sh
git commit -m "test: assert book reader typography and mobile layout"
```

---

### Task 2: Update The Theme Head And Header Identity

**Files:**
- Modify: `theme/index.hbs`
- Test: `scripts/test-site-render.sh`

- [ ] **Step 1: Swap the Google Fonts import from Lora to Literata**

将当前字体导入：

```hbs
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Lora:wght@400;500;600;700&display=swap">
```

替换为：

```hbs
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Literata:wght@400;500;600;700&display=swap">
```

- [ ] **Step 2: Add a subtle centered book identity without changing content plumbing**

在 `header .book-toolbar` 中间加入一个只负责视觉层级的轻量 center 区块，保持现有左侧 toggle/home 与右侧 search/contact 控件不变：

```hbs
<div class="toolbar-center book-reader-identity" aria-hidden="true">
    <span class="book-reader-title">{{ book_title }}</span>
</div>
```

插入位置：

```hbs
<div class="book-toolbar">
    <div class="toolbar-left">
        ...
    </div>

    <div class="toolbar-center book-reader-identity" aria-hidden="true">
        <span class="book-reader-title">{{ book_title }}</span>
    </div>

    {{#if search_enabled}}
    <div class="toolbar-search-slot hidden" aria-hidden="true"></div>
    {{/if}}

    <div class="toolbar-right">
        ...
    </div>
</div>
```

说明：

- 不改 `{{{ content }}}`
- 不改 `id="mdbook-sidebar"`
- 不改搜索与 overlay 的 id
- 不新增新的产品功能按钮

- [ ] **Step 3: Run the render test to verify the failure moves to CSS**

Run:

```bash
npm run test:site
```

Expected: FAIL on CSS markers such as `--reader-serif` or mobile pagination rules, rather than the font import.

- [ ] **Step 4: Commit the template update**

```bash
git add theme/index.hbs
git commit -m "feat: refresh book reader font import and header identity"
```

---

### Task 3: Introduce The Serif Reading System On Desktop

**Files:**
- Modify: `theme/custom.css`
- Test: `scripts/test-site-render.sh`

- [ ] **Step 1: Add explicit sans and serif tokens near the top of the file**

在 `:root` 变量区加入：

```css
:root {
  --reader-sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --reader-serif: "Literata", Georgia, serif;
  --reader-body-size: 17px;
  --reader-body-leading: 1.68;
  --reader-body-tracking: 0.005em;
}
```

- [ ] **Step 2: Keep chrome sans, but move long-form reading to serif**

将字体责任改成下面这种分工：

```css
html,
body {
  font-family: var(--reader-sans);
}

.reader-article,
.reader-article p,
.reader-article li,
.reader-article blockquote {
  font-family: var(--reader-serif);
  font-size: var(--reader-body-size);
  line-height: var(--reader-body-leading);
  letter-spacing: var(--reader-body-tracking);
}

.content h1,
.content h2,
.content h3,
.content h4,
.content h5,
.content h6 {
  font-family: var(--reader-serif);
  font-weight: 500;
  letter-spacing: -0.01em;
}

.book-toolbar,
.menu-title,
.chapter,
.chapter-nav-card,
.book-outline-body,
#mdbook-searchbar,
#mdbook-searchresults,
.reference-index,
.reference-glossary-list,
.reader-article table,
.reader-article thead,
.reader-article tbody,
.reader-article th,
.reader-article td {
  font-family: var(--reader-sans);
}
```

- [ ] **Step 3: Raise the desktop reading hierarchy to match the approved mock**

将当前偏小的桌面层级调整为更接近书籍阅读器：

```css
.content main {
  max-width: none;
  font-size: var(--reader-body-size);
  line-height: var(--reader-body-leading);
}

.content p {
  max-width: var(--content-max-width);
  margin-bottom: 1.2rem;
  color: var(--ink);
  line-height: var(--reader-body-leading);
}

.content h1 {
  margin-top: 0;
  padding-bottom: 0;
  border-bottom: 0;
  color: var(--ink);
  font-size: clamp(2.6rem, 2rem + 1.5vw, 3.35rem);
  line-height: 1.04;
  text-wrap: balance;
}

.content h2 {
  margin-top: 3rem;
  margin-bottom: 0.9rem;
  color: var(--ink);
  font-size: clamp(1.8rem, 1.55rem + 0.5vw, 2.15rem);
  line-height: 1.18;
}

.content h3 {
  margin-top: 1.85rem;
  margin-bottom: 0.65rem;
  color: var(--ink);
  font-size: clamp(1.35rem, 1.2rem + 0.3vw, 1.55rem);
  line-height: 1.22;
}
```

- [ ] **Step 4: Add the centered toolbar identity styling**

在 toolbar 区域新增：

```css
.book-reader-identity {
  min-width: 0;
  flex: 1 1 auto;
  display: flex;
  justify-content: center;
  pointer-events: none;
}

.book-reader-title {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 0;
  max-width: 42rem;
  color: var(--ink);
  font-family: var(--reader-sans);
  font-size: 0.95rem;
  font-weight: 500;
  line-height: 1.2;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
```

- [ ] **Step 5: Run the render test to verify typography is green**

Run:

```bash
npm run test:site
```

Expected: PASS for font import and typography-family checks; FAIL only if later responsive tasks are not yet implemented.

- [ ] **Step 6: Commit the desktop typography pass**

```bash
git add theme/custom.css
git commit -m "feat: add serif reading system to book reader"
```

---

### Task 4: Protect Scan-Heavy Surfaces From Becoming Too Literary

**Files:**
- Modify: `theme/custom.css`
- Test: `scripts/test-site-render.sh`

- [ ] **Step 1: Keep analytical surfaces in sans-serif and tighten their density**

为表格、索引、术语页、图表 caption 加明确的 sans 规则，避免正文 serif 把扫描型页面拖慢：

```css
.reader-article table,
.reader-article th,
.reader-article td,
.reference-index,
.reference-index-list,
.reference-index-link,
.reference-glossary-list,
.reference-glossary-item,
.figure-caption,
.chapter-nav-label {
  font-family: var(--reader-sans);
}

.reader-article table th {
  font-size: 0.84rem;
  font-weight: 600;
  letter-spacing: 0.01em;
}

.reader-article table td {
  font-size: 0.95rem;
  line-height: 1.45;
}

.reference-index-intro,
.reference-index-link,
.reference-glossary-item dd {
  font-size: 0.98rem;
  line-height: 1.55;
}
```

- [ ] **Step 2: Make the formula and callout surfaces match the new reading system**

针对 Chapter 4 的公式与说明卡片，加入：

```css
.reader-article .book-formula,
.reader-article .book-formula *,
.reader-article .callout,
.reader-article .callout * {
  font-family: inherit;
}

.reader-article .math,
.reader-article .formula-line {
  font-family: var(--reader-serif);
}

.reader-article .formula-meta,
.reader-article .formula-note {
  font-family: var(--reader-sans);
}
```

如果文件里当前没有这些类名，不要新造功能结构；执行时只对现有相近的公式/卡片类做等价映射。

- [ ] **Step 3: Preserve auxiliary pages as scan-friendly rather than prose-heavy**

对 cover、list-of-figures、list-of-tables、abbreviations、glossary 这几类页面执行下面的原则：

```css
body.book-page-aux-index .reader-article,
body.book-page-abbreviations .reader-article,
body.book-page-glossary .reader-article {
  font-family: var(--reader-sans);
}
```

如果当前页面分类 class 与上面名字不同，执行时用现有 `body.book-page-*` 分类名对齐，不新增内容分类逻辑。

- [ ] **Step 4: Run the render test**

Run:

```bash
npm run test:site
```

Expected: PASS for `reference-index`, `reference-glossary-list`, and `reader-article table` font-family checks.

- [ ] **Step 5: Commit the analytical-surface pass**

```bash
git add theme/custom.css
git commit -m "feat: keep analytical book surfaces scan-friendly"
```

---

### Task 5: Apply The Confirmed Responsive Rules

**Files:**
- Modify: `theme/custom.css`
- Test: `scripts/test-site-render.sh`

- [ ] **Step 1: Keep the current desktop-to-medium collapse model**

保留并明确中屏逻辑：

```css
@media (max-width: 1280px) {
  .reader-layout {
    grid-template-columns: minmax(0, 1fr);
  }

  .reader-outline {
    display: none;
  }
}
```

- [ ] **Step 2: Reduce header and content density on tablet widths**

在 `@media (max-width: 1080px)` 中，收紧页头与正文外边距，同时隐藏中间书名区，避免顶栏拥挤：

```css
@media (max-width: 1080px) {
  .book-toolbar,
  .reader-layout,
  .book-progress {
    width: 100%;
  }

  .book-toolbar {
    padding: 0 1rem;
  }

  .book-reader-identity {
    display: none;
  }

  .reader-main {
    padding: 24px 20px 40px;
  }
}
```

- [ ] **Step 3: Convert mobile into the approved single-column reader**

在 `@media (max-width: 760px)` 中，执行完整的窄屏落地：

```css
@media (max-width: 760px) {
  :root {
    --reader-body-size: 16.25px;
    --reader-body-leading: 1.7;
  }

  .content {
    padding-bottom: 2rem;
  }

  .reader-layout {
    padding: 1.5rem 1rem 2rem;
  }

  .reader-main {
    padding: 0;
  }

  .content h1 {
    font-size: clamp(2rem, 1.7rem + 1vw, 2.35rem);
    line-height: 1.08;
  }

  .content h2 {
    font-size: 1.6rem;
  }

  .chapter-pagination {
    flex-direction: column;
    align-items: stretch;
    gap: 0.8rem;
  }

  .chapter-nav-card {
    flex: none;
    width: 100%;
    gap: 0.6rem;
    padding: 14px 16px 14px;
  }

  .chapter-nav-placeholder {
    display: none;
  }

  .chapter-nav-next {
    text-align: left;
  }

  .chapter-nav-next .chapter-pagination-eyebrow {
    flex-direction: row;
  }

  .chapter-nav-next .chapter-pagination-eyebrow,
  .chapter-nav-next .chapter-nav-body {
    align-self: flex-start;
  }

  .reader-article table {
    display: block;
    width: 100%;
    overflow-x: auto;
    white-space: nowrap;
  }
}
```

- [ ] **Step 4: Run the render test to verify mobile rules are green**

Run:

```bash
npm run test:site
```

Expected: PASS with the new mobile stacking and `text-align: left;` assertions.

- [ ] **Step 5: Commit the responsive pass**

```bash
git add theme/custom.css
git commit -m "feat: align book reader responsive behavior to approved mock"
```

---

### Task 6: Verify Whether JavaScript Needs A Minimal Patch

**Files:**
- Modify if needed: `theme/custom.js`
- Test: `scripts/test-site-render.sh`

- [ ] **Step 1: Run the site render test before changing JavaScript**

Run:

```bash
npm run test:site
```

Expected: PASS. If it passes, do not edit `theme/custom.js`.

- [ ] **Step 2: Only if visual verification shows regressions, patch JS minimally**

允许的最小 JS 修补范围：

```js
// 仅在以下问题出现时修补：
// 1. progress line no longer follows the actual scroll container
// 2. hash links no longer land correctly inside the article scroller
// 3. generated On This Page block is not mounted into .book-outline-body
```

不允许在这个任务中：

- 增加新产品逻辑
- 改变 `/book` 默认跳转逻辑
- 引入新的 UI 状态机

- [ ] **Step 3: If JS changed, re-run the render test**

Run:

```bash
npm run test:site
```

Expected: PASS.

- [ ] **Step 4: Commit only if JS actually changed**

```bash
git add theme/custom.js
git commit -m "fix: preserve book reader scroll and outline behavior"
```

---

### Task 7: Final Verification And Handoff

**Files:**
- Verify: `theme/index.hbs`
- Verify: `theme/custom.css`
- Verify: `theme/custom.js`
- Verify: `scripts/test-site-render.sh`

- [ ] **Step 1: Run the full book render verification**

Run:

```bash
npm run test:site
```

Expected: PASS.

- [ ] **Step 2: Run the production build**

Run:

```bash
npm run build
```

Expected: PASS with generated book output under `book/`.

- [ ] **Step 3: Manually verify the three key states**

检查以下三类页面：

- `public/book/index.html` 或默认落到首个章节的阅读页：确认 serif 正文、三栏宽屏结构、细进度条、安静右栏。
- `public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html`：确认表格可扫读、公式块不失真、上一章/下一章桌面同一行。
- 窄视口下的同一章节页：确认正文单列、右栏隐藏、目录依旧由 menu 控制、上一章/下一章纵向堆叠且左对齐。

- [ ] **Step 4: Commit the verification-only checkpoint**

```bash
git add theme/index.hbs theme/custom.css scripts/test-site-render.sh
git commit -m "feat: finalize book reader typography and responsive refresh"
```

---

## Spec Coverage Check

- 宽屏定向设计：由 Task 2、Task 3、Task 4 覆盖。
- 窄屏定向设计：由 Task 5 覆盖。
- 正文 serif + UI sans：由 Task 3、Task 4 覆盖。
- 不改正文文本：全计划仅触碰 theme 和 test 文件，未包含 `src/**/*.md`。
- `Previous/Next` 窄屏堆叠：由 Task 5 明确覆盖。
- 表格、术语表、figure/table index 保持 scan-friendly：由 Task 4 覆盖。

## Placeholder Scan

- 无 `TODO`、`TBD`、`implement later`。
- 所有改动文件路径均为精确路径。
- 所有执行命令均为精确命令。

## Type And Selector Consistency Check

- serif token 统一为 `--reader-serif`
- sans token 统一为 `--reader-sans`
- 移动端分页容器统一为 `.chapter-pagination`
- 移动端卡片统一为 `.chapter-nav-card`
- 中间标题区统一为 `.book-reader-identity` / `.book-reader-title`

## Execution Note

本计划默认 **先执行 CSS 和模板，不改 JS**。只有在最终验证证明 progress、hash scroll 或 outline 挂载回归时，才触碰 `theme/custom.js`。

**Plan complete and saved to `docs/superpowers/plans/2026-06-04-book-reader-typography-responsive-refresh.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
