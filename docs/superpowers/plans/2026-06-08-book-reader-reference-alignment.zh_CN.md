# Book 阅读器参考对齐实施方案

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**目标：** 在不破坏 mdBook 作为内容引擎的前提下，把已批准的宽屏与窄屏阅读器参考稿落地到 mdBook 阅读器中，使真实 `/book/` 体验在学术专著式阅读壳、导航层级、logo 行为和知识对象样式上对齐目标设计。

**架构：** 继续以 `theme/index.hbs` 作为唯一阅读壳模板，`theme/custom.css` 作为布局 token 与响应式组件样式的唯一事实来源，`theme/custom.js` 作为移动端派生 chrome、页内目录落位与图表增强的轻量 DOM 编排层。不要机械照抄 mock；当真实内容与 mock 不一致时，应将已批准的设计系统投射到真实书籍结构上，并在代表性 figure、table、formula 章节上验证。

**技术栈：** mdBook、Handlebars 主题模板、CSS、原生 JavaScript、基于 shell 的渲染断言

---

## 第一性原理

1. **阅读优先。** 用户打开书页的首要目标是阅读长文；导航和工具的存在是为了降低认知负担，而不是争夺注意力。
2. **品牌连续性必须传达可信度，而不是新奇感。** 阅读器页头必须使用与 landing page 相同的 `Upstream Atlas` 资产家族。Book 是同一产品的延续，不是另一个站点。
3. **知识对象必须有稳定语义。** 公式、图片、表格不是装饰块，而是带 caption、note 和跨端连续性的学术参考对象。
4. **响应式行为必须保留语义。** 移动端是同一阅读器的变体，不是第二套产品。相同对象应跨断点保留，只调整容器与导航承载方式。
5. **源内容保真优先于 mock 字面一致。** 已批准截图是阅读壳、层级与组件处理方式的参考设计。当真实章节语料与 mock 文案或对象顺序不一致时，应保留设计系统，并将其映射到真实章节内容，而不是杜撰新的编辑内容。

## MECE 工作流拆分

1. **阅读壳与品牌**
   - Header、logo 尺寸、sidebar、progress bar、页面背景、分页壳层。
2. **导航与定位**
   - 桌面端 sidebar 行为、桌面端 outline rail、移动端 chapter bar、移动端内联 “On this page”。
3. **知识对象系统**
   - 公式面板、figure 卡片、table 卡片、caption、notes、文图配对。
4. **响应式变换**
   - Desktop 到 tablet 到 mobile 的布局规则、组件身份延续与密度调优。
5. **验证与发布安全**
   - 源码断言、生成物断言、代表性章节的人工视觉 QA。

## 非目标

- 不要手工编辑 `public/`。
- 不要重写 landing page。
- 不要为了强行贴合 mock 标题 “Overview of the Upstream Petroleum Industry” 而改动真实章节语料。
- 不要在现有已编写公式内容足以满足公式设计验收的前提下，再虚构新的章节级公式。
- 不要用客户端框架取代 mdBook 的导航、搜索或内容生成。

## 真实内容与 Mock 的关系

已批准的宽屏与窄屏参考稿展示的是一个概念性章节页。仓库中的真实内容 **并不包含** 这个完全一致的章节标题。最合理的实施策略是：

- 把参考稿作为阅读壳、品牌、布局和知识对象处理方式的事实来源
- 在 `chapter-01-value-chain-of-the-hydrocarbon-sector` 上验证壳层 + 图片 + 表格
- 在 `glossary`、`chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states`、`chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries` 上验证公式处理

如果产品后续希望把公式块显式插入 `chapter-01`，应将其视为**独立的编辑 / parity 决策**，不属于本次阅读壳对齐方案的一部分。

## 文件地图

- `theme/index.hbs:127-239`
  - 负责静态阅读壳，并需要暴露仅供移动端派生 chrome 使用的占位节点。
- `theme/custom.css:17-224`
  - 负责全局阅读器 token、壳层几何关系、排版和 light theme 调色。
- `theme/custom.css:549-910`
  - 负责 toolbar、logo 尺寸、search slot、sidebar、outline rail 与 pagination card 样式。
- `theme/custom.css:1347-1888`
  - 负责 formulas、figures、tables、captions 以及学术对象样式。
- `theme/custom.css:1925-2023`
  - 负责 outline、pagination 与 header logo 切换的断点收敛逻辑。
- `theme/custom.js:159-650`
  - 负责 outline 归一化、figure/table 包装、search slot 编排与 page variant glue。
- `scripts/test-site-render.sh:407-1035`
  - 负责源码与生成书页输出的构建时契约断言。
- **代表性生成验收页面**
  - `public/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html`
  - `public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html`
  - `public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html`
  - `public/book/chapters/glossary.html`

## 需要实现的视觉契约

### Desktop / Wide Reference

- Header 使用与 landing page 一致的完整 `Upstream Atlas` lockup。
- 左侧 chapter rail 仍是主导航对象。
- 中间阅读列保持绝对的视觉主导地位。
- 右侧 rail 退居为安静的 “On This Page” 参考面板。
- Formula、figure、table 三类对象共享同一套 academic publication 视觉语言。

### Narrow / Mobile Reference

- 使用同一品牌家族，但 header 改为 compact icon。
- Header 下方的 chapter context bar 替代常驻 sidebar。
- “On This Page” 转为正文流中的 inline card。
- Figures 与 tables 在移动端仍保持与桌面端相同的 card 身份，不发展出第二套移动端样式家族。
- Mobile 通过压缩密度保持学术感，而不是把对象拍平。

---

### Task 1：先把参考契约锁进渲染测试

**文件：**
- 修改：`scripts/test-site-render.sh`
- 测试：`scripts/test-site-render.sh`

- [ ] **Step 1：为新的移动端阅读壳占位与响应式契约加入失败断言**

在现有 `public/book/index.html`、`theme/index.hbs`、`theme/custom.css`、`theme/custom.js` 相关断言附近加入：

```sh
check_contains theme/index.hbs 'class="reader-mobile-chapter-bar hidden"'
check_contains theme/index.hbs 'class="reader-mobile-chapter-toggle"'
check_contains theme/index.hbs 'class="reader-mobile-outline-anchor"'
check_contains theme/custom.css '.reader-mobile-chapter-bar {'
check_contains theme/custom.css '.reader-mobile-chapter-toggle {'
check_contains theme/custom.css '.reader-mobile-outline-card {'
check_contains theme/custom.css '.reader-mobile-outline-card .on-this-page {'
check_contains theme/custom.js 'function installMobileChapterBar()'
check_contains theme/custom.js 'function installInlineOutlineCard()'
check_contains theme/custom.js 'document.querySelector(".reader-mobile-chapter-toggle")'
check_contains theme/custom.js 'document.querySelector(".reader-mobile-outline-anchor")'
check_contains theme/custom.css '--brand-blue: #3163c2;'
check_contains theme/custom.css '--brand-blue-deep: #264d97;'
check_contains theme/custom.css '--brand-gold: #d9b24a;'
```

- [ ] **Step 2：补充“logo 仍属同一家族”的契约断言**

保留现有 logo 资产断言，并在 CSS 源码中加入桌面 / 移动端尺寸检查：

```sh
check_contains theme/custom.css '.book-home-icon-full {'
check_contains theme/custom.css 'width: 138px;'
check_contains theme/custom.css '.book-home-icon-compact {'
check_contains theme/custom.css 'width: 24px;'
check_contains theme/custom.css 'height: 24px;'
```

- [ ] **Step 3：运行站点渲染测试，确认它会因新的移动壳要求而失败**

运行：

```bash
npm run test:site
```

预期：FAIL，报错类似 `class="reader-mobile-chapter-bar hidden"` 或 `.reader-mobile-outline-card {` 缺失，说明新的契约已真正被编码进测试。

- [ ] **Step 4：提交 red test**

```bash
git add scripts/test-site-render.sh
git commit -m "test: lock book reader reference contract"
```

### Task 2：为移动端阅读器 chrome 增加静态壳层锚点

**文件：**
- 修改：`theme/index.hbs:136-239`
- 测试：`scripts/test-site-render.sh`

- [ ] **Step 1：在 progress line 下方插入移动端 chapter bar 占位**

在 `theme/index.hbs` 中 progress bar 后、`#mdbook-content` 前插入：

```hbs
<div class="reader-mobile-chapter-bar hidden" aria-hidden="true">
    <button class="reader-mobile-chapter-toggle" type="button" aria-controls="mdbook-sidebar" aria-expanded="false">
        <span class="reader-mobile-chapter-icon">{{fa "regular" "book-open"}}</span>
        <span class="reader-mobile-chapter-kicker"></span>
        <span class="reader-mobile-chapter-title"></span>
        <span class="reader-mobile-chapter-chevron">{{fa "solid" "chevron-down"}}</span>
    </button>
</div>
```

- [ ] **Step 2：在文章列内部加入供 JS 填充移动端内联目录的锚点**

在 `.reader-article` 内、`{{{ content }}}` 前插入：

```hbs
<div class="reader-mobile-outline-anchor" hidden aria-hidden="true"></div>
```

- [ ] **Step 3：保持现有桌面壳层契约不变**

以下既有契约点 **不要** 改：

- `nav#mdbook-sidebar`
- `img.book-home-icon.book-home-icon-full`
- `img.book-home-icon.book-home-icon-compact`
- `div.toolbar-search-slot`
- `main#mdbook-reader-scroll`
- `aside#mdbook-outline-scroll`

- [ ] **Step 4：运行 render test，让失败转移到 CSS / JS**

运行：

```bash
npm run test:site
```

预期：FAIL，但失败点应该转为缺少 CSS selector 或 JS function，而不是模板标记缺失。

- [ ] **Step 5：提交壳层占位**

```bash
git add theme/index.hbs
git commit -m "feat: add mobile reader shell anchors"
```

### Task 3：重设阅读器壳层 Token，使其对齐已批准视觉系统

**文件：**
- 修改：`theme/custom.css:17-224`、`theme/custom.css:549-910`、`theme/custom.css:1925-2023`
- 测试：`scripts/test-site-render.sh`

- [ ] **Step 1：把顶层 reader token 对齐到 landing-page 家族**

更新 root token block，让 book shell 复用已批准调色，而不是继续使用旧的近似值：

```css
:root {
  --menu-bar-height: 56px;
  --reader-left-offset: 0px;
  --reader-sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --reader-serif: "Literata", Georgia, serif;
  --sidebar-width: 256px;
  --outline-width: 256px;
  --ink: #0b1f33;
  --muted: #526171;
  --paper: #ffffff;
  --panel: #ffffff;
  --line: rgba(11, 31, 51, 0.10);
  --line-strong: rgba(11, 31, 51, 0.18);
  --primary: #3163c2;
  --primary-deep: #264d97;
  --accent: #d88a1d;
  --brand-blue: #3163c2;
  --brand-blue-deep: #264d97;
  --brand-gold: #d9b24a;
  --deep: #0b1f33;
  --soft-blue: #eef2f4;
  --book-bg: #f7f8f9;
  --book-surface: rgba(255, 255, 255, 0.94);
  --book-surface-strong: #ffffff;
}
```

- [ ] **Step 2：严格保持桌面端 logo 尺寸与已批准稿一致**

Header logo 尺寸继续对齐 approved mock 与当前站点 shell：

```css
.book-home-icon-full {
  width: 138px;
}

.book-home-icon-compact {
  display: none;
  width: 24px;
  height: 24px;
}
```

- [ ] **Step 3：增加移动端壳层样式，但不削弱桌面端**

为新 chrome 补充 desktop-hidden / mobile-visible 规则：

```css
.reader-mobile-chapter-bar {
  display: none;
  border-bottom: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.98);
}

.reader-mobile-chapter-toggle {
  width: 100%;
  min-height: 48px;
  display: grid;
  grid-template-columns: auto auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 0.85rem;
  padding: 0.85rem 1rem;
  border: 0;
  background: transparent;
  color: var(--ink);
  font-family: var(--reader-sans);
  text-align: left;
}

.reader-mobile-outline-card {
  margin: 1rem 0 1.5rem;
  padding: 0.9rem 1rem;
  border: 1px solid rgba(11, 31, 51, 0.10);
  border-radius: 0.9rem;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.96) 100%);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.045);
}
```

- [ ] **Step 4：增加窄屏断点行为**

在现有 mobile breakpoints 中加入下列变换，而不是另起一套产品：

```css
@media (max-width: 1280px) {
  .reader-outline {
    display: none;
  }

  .reader-mobile-chapter-bar {
    display: block;
  }
}

@media (max-width: 900px) {
  .book-home-icon-full {
    display: none;
  }

  .book-home-icon-compact {
    display: block;
  }
}
```

- [ ] **Step 5：运行站点渲染测试**

运行：

```bash
npm run test:site
```

预期：FAIL，且只剩 JS hook 或运行期壳层编排未完成。

- [ ] **Step 6：提交 token 与壳层 CSS**

```bash
git add theme/custom.css
git commit -m "feat: align book reader shell tokens and mobile chrome"
```

### Task 4：在 JS 中实现移动端章节上下文与内联目录

**文件：**
- 修改：`theme/custom.js:560-650`
- 测试：`scripts/test-site-render.sh`

- [ ] **Step 1：增加一个从真实 mdBook sidebar 解析当前章节的 helper**

在 `moveOutline()` 附近加入：

```js
function getActiveSidebarChapterLink() {
  return (
    document.querySelector("#mdbook-sidebar a.active") ||
    document.querySelector("#mdbook-sidebar a.current-header")
  );
}
```

- [ ] **Step 2：用真实 sidebar 状态实现 `installMobileChapterBar()`**

加入以下函数：

```js
function installMobileChapterBar() {
  const bar = document.querySelector(".reader-mobile-chapter-bar");
  const toggle = document.querySelector(".reader-mobile-chapter-toggle");
  const kicker = document.querySelector(".reader-mobile-chapter-kicker");
  const title = document.querySelector(".reader-mobile-chapter-title");
  const sidebarToggle = document.getElementById("mdbook-sidebar-toggle-anchor");
  const activeLink = getActiveSidebarChapterLink();

  if (!bar || !toggle || !kicker || !title || !sidebarToggle || !activeLink) {
    return;
  }

  const normalizedTitle = (activeLink.textContent || "").replace(/\s+/g, " ").trim();
  kicker.textContent = "Chapter";
  title.textContent = normalizedTitle;
  bar.classList.remove("hidden");
  bar.setAttribute("aria-hidden", "false");

  toggle.addEventListener("click", function () {
    sidebarToggle.checked = !sidebarToggle.checked;
    toggle.setAttribute("aria-expanded", sidebarToggle.checked ? "true" : "false");
  });

  toggle.setAttribute("aria-expanded", sidebarToggle.checked ? "true" : "false");
}
```

- [ ] **Step 3：通过克隆规范化后的 outline，把它渲染到文章流中的 `installInlineOutlineCard()`**

加入以下函数：

```js
function installInlineOutlineCard() {
  const anchor = document.querySelector(".reader-mobile-outline-anchor");
  const outline = document.querySelector(".book-outline-body .on-this-page");

  if (!anchor || !outline) {
    return;
  }

  const card = document.createElement("section");
  const label = document.createElement("p");
  const body = outline.cloneNode(true);

  card.className = "reader-mobile-outline-card";
  label.className = "book-outline-label";
  label.textContent = "On This Page";
  card.appendChild(label);
  card.appendChild(body);

  anchor.hidden = false;
  anchor.removeAttribute("aria-hidden");
  anchor.replaceChildren(card);
}
```

- [ ] **Step 4：把两个函数接入现有启动流**

在 `DOMContentLoaded` 分支中，`moveOutline();` 后面调用：

```js
installMobileChapterBar();
installInlineOutlineCard();
```

- [ ] **Step 5：运行站点渲染测试**

运行：

```bash
npm run test:site
```

预期：PASS，如果此前缺的只是这些新的 JS hook。

- [ ] **Step 6：提交阅读器编排逻辑**

```bash
git add theme/custom.js
git commit -m "feat: add mobile chapter context and inline outline"
```

### Task 5：把 Figures、Tables、Formulas 规范成同一学术对象家族

**文件：**
- 修改：`theme/custom.css:1347-1888`
- 修改：`theme/custom.js:200-520`
- 测试：`scripts/test-site-render.sh`

- [ ] **Step 1：确保 formulas、figures、tables 共用同一套视觉语法**

三类对象必须保持以下统一特征：

- formula block 使用 white-to-soft-blue paper gradients、细蓝色左规则线、克制阴影
- figure card 使用圆角白色壳层、带框 media area、细分隔线、蓝色 label、衬线 caption 文本
- table shell 使用同样的白色壳层、轻边框、柔和阴影、蓝色 label、衬线 caption 文本和底部 note

**不要** 再分裂出第二套 mobile-only 对象语言。

- [ ] **Step 2：把已有富公式章节继续作为公式验收面**

不要向 `chapter-01` 人工插入虚构公式 markup。公式样式如需校准，优先对照：

- `public/book/chapters/glossary.html`
- `public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html`
- `public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html`

公式样式应继续由现有源码标记驱动，例如：

```html
<div class="book-formula api-density-formula" role="img" aria-label="API density equals 141.5 divided by Density at 15 degrees Celsius minus 131.5">
```

以及：

```html
<section class="formula-panel formula-panel--r-factor" aria-label="R-factor calculation formulas">
```

- [ ] **Step 3：保持移动端图片与表格仍然是 card，而不是被拍平**

在 `@media (max-width: 760px)` 下，确保以下行为继续成立：

```css
.figure-card {
  margin: 1.25rem 0 1.5rem;
}

.figure-media {
  padding: 0.75rem;
}

.table-anchor-shell {
  border-radius: 1rem;
}

.table-scroll {
  padding: 0.65rem;
}
```

移动端可以把 grid collapse 成一列，但不能去掉 card shell、caption 或 note 处理。

- [ ] **Step 4：保留 figure / table 语义包装的 JS 包装逻辑**

在需要微调的前提下，继续保留这些行为：

- `annotateFigureCaptions()`
- `annotateTables()`
- `enhanceTable6()`

以下现有 wrapper 创建路径不能退化：

```js
wrapper.className = "figure-card figure-anchor-target";
tableShell.className = "table-anchor-shell";
tableScroll.className = "table-scroll";
caption.className = "table-caption";
```

- [ ] **Step 5：运行站点渲染测试**

运行：

```bash
npm run test:site
```

预期：PASS，包括脚本中已经存在的 formula / figure / table 断言。

- [ ] **Step 6：提交学术对象归一化改动**

```bash
git add theme/custom.css theme/custom.js
git commit -m "feat: unify academic content objects across breakpoints"
```

### Task 6：对宽屏与窄屏验收面进行视觉 QA

**文件：**
- 除非 QA 发现问题，否则不需要额外源码修改
- 测试：`scripts/test-site-render.sh`

- [ ] **Step 1：构建站点**

运行：

```bash
npm run build:site
```

预期：PASS，并重新生成 `public/book/` 输出。

- [ ] **Step 2：再次运行 render contract**

运行：

```bash
npm run test:site
```

预期：输出 `Site render checks passed.`

- [ ] **Step 3：对代表性页面进行人工视觉 QA**

在本地浏览器或 in-app browser 中检查以下页面：

- `public/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html`
- `public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html`
- `public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html`
- `public/book/chapters/glossary.html`

桌面端 QA checklist：

- 完整 logo lockup 的尺寸和层级与宽屏 approved reference 一致，且保持克制
- sidebar 是唯一的左侧导航面
- 右侧 outline 只是安静的辅助 rail
- figure、formula、table 三类 card 的学术语言一致

移动端 QA checklist：

- compact icon 干净替代 full logo
- header 下出现 chapter context bar
- 正文流中出现 inline “On This Page” card
- figures 与 tables 保持 card 状态，而不是被拍平
- 不出现重复或互相冲突的导航面

- [ ] **Step 4：提交最终验证通过的状态**

```bash
git add theme/index.hbs theme/custom.css theme/custom.js scripts/test-site-render.sh
git commit -m "feat: align book reader to approved desktop and mobile references"
```

## 执行过程中需要当场做出的决策与风险

1. **Mock 与真实内容不一致**
   - 决策：实现 mock 中的壳层与对象系统，但保留 mdBook 中真实的章节标题与内容顺序。
2. **“chapter-01 一定要有公式”的压力**
   - 决策：本方案不向 `chapter-01` 注入新的公式内容；公式样式验收依托已有富公式章节完成。
3. **Sidebar 重复的风险**
   - 决策：继续把 `nav#mdbook-sidebar` 作为唯一左导航面；移动端 context bar 只是派生摘要 / toggle，不是第二棵导航树。
4. **移动端被拍平的风险**
   - 决策：折叠的是 layout，而不是组件身份。Figures 与 tables 在移动端仍保留桌面端家族样式。

## 完成定义

- Desktop reader shell 在层级、品牌连续性和知识对象处理方式上对齐已批准的宽屏 reference。
- Mobile reader shell 在结构、logo 行为和内联导航策略上对齐已批准的窄屏 reference。
- Figure、formula、table 组件在所有断点共享同一套学术视觉系统。
- mdBook 仍是唯一的内容与导航引擎。
- `npm run test:site` 通过。
- 没有对 `public/` 进行直接编辑。

## 建议用于新 Thread 的执行 Prompt

```text
请在 /Users/edison/workspace/peakwalk/scm/gitlab/africa-book 仓库中执行这份方案：

docs/superpowers/plans/2026-06-08-book-reader-reference-alignment.md

要求：
1. 先完整阅读该计划，再开始实施，不要重新写方案。
2. 按计划中的 first principles、MECE workstreams、non-goals 和 file map 执行。
3. 严格保留 mdBook 作为唯一内容与导航引擎，不要编辑 public/。
4. 如果 mock 与真实章节内容冲突，以计划中的 “Source Reality vs. Mock Reality” 为准。
5. 优先执行 shell、responsive chrome、figure/table/formula 对齐，不要把精力转移到 landing page 或其他页面。
6. 执行完成后必须运行计划中的验证命令，至少包括 `npm run test:site`，并汇报通过情况、剩余风险和任何偏离计划的决策。

如果你选择按任务逐项执行，请使用 superpowers:executing-plans；如果你选择分任务派发，请使用 superpowers:subagent-driven-development。
```

Plan complete and saved to `docs/superpowers/plans/2026-06-08-book-reader-reference-alignment.zh_CN.md`.
