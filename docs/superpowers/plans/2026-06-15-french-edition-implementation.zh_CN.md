# 法文版实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在当前英文版旁边新增法文 landing page 和法文 mdBook 版本，在 landing header 与 book header 中提供语言切换入口，让 neutral entry routes 默认停留在英文版并在浏览器偏好法语时跳转到法文入口，同时让它们基于法文 DOCX/PDF 手稿输入完成发布与校验。

**Architecture:** 保持 locale-specific 内容位于并行源目录中，但让所有 build、reader 后处理、parity 和 figure 脚本都通过一个共享 edition registry 具备 edition-aware 能力。英文继续发布在根路径，法文发布在 `/fr` 下，并在两个语言版本之间保持 chapter slug 与 figure numbering 对齐。

**Tech Stack:** Node.js 构建脚本、mdBook、Handlebars theme templates、Python parity/figure 脚本、shell 渲染断言、OpenSpec 规划产物

---

## Source of Truth

这份文档是执行计划，不是规范层面的唯一设计真相源。

本次变更的权威规划文档是：

- OpenSpec proposal：`openspec/changes/add-french-edition/proposal.md`
- OpenSpec specs：
  - `openspec/changes/add-french-edition/specs/localized-site-editions/spec.md`
  - `openspec/changes/add-french-edition/specs/localized-book-sources/spec.md`
  - `openspec/changes/add-french-edition/specs/localized-parity-validation/spec.md`
- OpenSpec design：`openspec/changes/add-french-edition/design.md`
- OpenSpec tasks：`openspec/changes/add-french-edition/tasks.md`

如果这份计划和 OpenSpec change artifacts 发生冲突，应以 OpenSpec 文件为准，并回头更新这份计划，而不是把它当成第二份并行设计文档。

---

## Solution Summary

### File Map

- Create: `src-fr/`
  法文 landing、legal、chapters、images 和 summary 内容根目录。
- Create: `book.fr.toml`
  法文 mdBook 配置。
- Create: `resources/editions/en/reference.docx`
- Create: `resources/editions/en/reference.pdf`
- Create: `resources/editions/fr/reference.docx`
- Create: `resources/editions/fr/reference.pdf`
  构建与校验命令使用的稳定手稿别名路径。
- Create: shared edition registry 和 locale catalogs
  routes、labels、source paths、manuscript aliases 与 validation rules 的统一数据源。
- Modify: `scripts/generate-index-page.mjs`
- Modify: `scripts/generate-legal-pages.mjs`
- Modify: `scripts/generate-chapters-page.mjs`
- Modify: `scripts/shared/landing-shell.mjs`
  让公开页面生成具备 edition-aware 能力，增加可见的 landing header 语言切换入口，并支持 neutral-entry 语言跳转。
- Modify: `theme/index.hbs`
- Modify: `theme/custom.js`
- Modify: `scripts/build_reader_page_meta.mjs`
- Modify: `scripts/build_static_reader_sidebar.mjs`
  让 reader shell 具备 locale-aware 能力，增加可见的 book header 语言切换入口，并支持 neutral-entry 的 book 跳转。
- Modify: `scripts/check_docx_parity.py`
- Modify: `scripts/check_docx_figures.py`
- Modify: `scripts/docx_parity/*`
- Modify: `scripts/docx_figures/*`
  让校验逻辑具备 edition-aware 能力。
- Replace: `src-fr/images` 软链为真实的 locale-owned 目录
  让法文 figure assets 能脱离 `src/images` 独立校验和重渲染。
- Modify: `package.json`
- Modify: `scripts/test-site-render.sh`
- Modify: `.github/workflows/pages.yml`
  双版本编排与发布 gate。

### Rollout Order

1. 稳定输入与配置。
2. 增加法文内容树。
3. 重构公开页面生成。
4. 增加法文 mdBook 构建与 reader 本地化。
5. 重构校验与 figure 脚本。
6. 将双版本校验提升到发布 gate。

---

### Task 1: Stabilize edition inputs and shared configuration

**Files:**
- Create: `resources/editions/` 下的 canonical manuscript aliases
- Create: shared edition registry 和 locale catalogs
- Modify: `package.json`

- [ ] **Step 1: Add canonical manuscript aliases**
为英文与法文 DOCX/PDF 输入创建稳定别名，并确保后续所有命令都不再直接依赖原始描述性文件名。

- [ ] **Step 2: Add the shared edition registry**
定义每个版本的 locale code、route prefix、source root、legal root、figure root、manifest path、book config path 和 validation metadata。

- [ ] **Step 3: Add edition-aware npm entrypoints**
把 `package.json` 中所有写死手稿路径和源根目录的命令改成 edition-aware 的构建/校验入口，并增加一个同时运行两个版本的顶层命令。

- [ ] **Step 4: Verify config readability**
运行最小 smoke command，分别在 Node 与 Python 环境中加载 registry，并确认两个版本都能解析出正确路径。

### Task 2: Add the French source tree with mirrored topology

**Files:**
- Create: `src-fr/SUMMARY.md`
- Create: `src-fr/index-main.html`
- Create: `src-fr/legal/*.json`
- Create: `src-fr/chapters/*.md`
- Create: `src-fr/images/*`
- Create: `book.fr.toml`

- [ ] **Step 1: Mirror the English topology**
创建法文源根目录，并与英文版保持一致的 chapter filenames、legal page keys 和 figure numbering。

- [ ] **Step 2: Add French landing and legal content**
翻译或先补齐法文 landing 与 legal 文案，同时保持当前生成脚本所需的结构槽位不变。

- [ ] **Step 3: Add French chapter and figure sources**
将法文章节 Markdown、summary、figure 资源和 figure manifest 目标都放入 `src-fr/`，且不改动英文源路径。

- [ ] **Step 4: Verify slug parity**
对 `src/chapters` 与 `src-fr/chapters` 做路径级比对，确认 slug 集合完全一致。

### Task 3: Refactor public-page generation and shell links

**Files:**
- Modify: `scripts/shared/landing-shell.mjs`
- Modify: `scripts/generate-index-page.mjs`
- Modify: `scripts/generate-legal-pages.mjs`
- Modify: `scripts/generate-chapters-page.mjs`

- [ ] **Step 1: Make shell links, labels, and the landing-header switch edition-aware**
把公开页面标签、路由构造以及 header-level 语言切换目标迁移到 edition-aware 数据层，使共享 shell 能正确渲染英文与法文。

- [ ] **Step 2: Make page generators edition-aware**
重构 landing、legal 与 chapter-library 生成器，让它们能接受 edition context 并写出对应版本的输出目录。

- [ ] **Step 3: Add neutral landing-route browser-language detection**
实现 landing 入口路由逻辑：在 neutral route 上保持英文为默认输出，但当浏览器偏好法语时跳转到 `/fr/`。

- [ ] **Step 4: Assemble per-edition assets**
更新站点装配逻辑，把共享静态资源复制到 `public/assets` 和 `public/fr/assets`。

- [ ] **Step 5: Verify generated public routes**
运行站点构建，确认英文根路径页面与法文 `/fr/` 页面都存在，并且文案、链接、landing header 语言切换目标和 neutral-entry 跳转行为都正确。

### Task 4: Add French mdBook build and reader-shell localization

**Files:**
- Modify: `theme/index.hbs`
- Modify: `theme/custom.js`
- Modify: `scripts/build_reader_page_meta.mjs`
- Modify: `scripts/build_static_reader_sidebar.mjs`
- Modify: 与 `mdbook build` 相关的编排逻辑
- Create: reader 流水线需要的任何 locale injection helper

- [ ] **Step 1: Add the French book config and build target**
接入 `book.fr.toml`，使法文内容能够发布到 `/fr/book`，同时保证英文版继续发布在 `/book`。

- [ ] **Step 2: Inject localized reader strings and book-header switch targets**
为 toolbar、search、outline、previous/next navigation 以及可见的 book header 语言切换入口注入本地化字符串和目标，而不复制整套 theme。

- [ ] **Step 3: Keep chapter mapping deterministic**
利用镜像 slug，使 reader meta、page variants 和 language switching 在两个版本中都不需要额外的路由映射表。

- [ ] **Step 4: Add neutral book-route browser-language detection**
实现 book 入口路由逻辑：在 neutral route 上保持英文为默认输出，但当浏览器偏好法语时跳转到 `/fr/book/`。

- [ ] **Step 5: Verify localized reader output**
检查生成后的 `/book` 与 `/fr/book` 输出，确认 shell 字符串、可见的 book header 语言切换入口和 neutral-entry 跳转行为分别符合英文和法文预期。

### Task 5: Refactor parity and figure validation for edition awareness

**Files:**
- Modify: `scripts/check_docx_parity.py`
- Modify: `scripts/check_docx_figures.py`
- Modify: `scripts/docx_parity/*`
- Modify: `scripts/docx_figures/*`

- [ ] **Step 1: Externalize chapter and anchor rules**
把英文专用的解析常量改成 edition-driven 数据，使法文章节提取能识别完整结构。

- [ ] **Step 2: Scope figure inventory by edition**
让 figure manifest generation 和 figure validation 都读取目标版本自己的 summary、chapter root、figure root、manuscript aliases 与 replacement-map 设置。

- [ ] **Step 3: Replace the French image-root symlink with a real directory**
把 `src-fr/images` 落成真实的 locale-owned 根目录，使法文 manifest 和 renderers 不再依赖共享英文图片树。

- [ ] **Step 4: Re-render French published figures from French manuscripts**
按 figure kind 用法文 DOCX/PDF 输入替换 bootstrap 法文图片，直到法语 web 图与法语手稿在内容和布局上对齐。

- [ ] **Step 5: Add per-edition verification commands**
暴露英文专用、法文专用和双版本联合校验命令。

- [ ] **Step 6: Verify failure surfaces**
在法文手稿路径上运行法文 parity/figure 命令，并确认失败输出指向的是法文章节/figure 位置，而不是英文路径。

### Task 6: Promote dual-edition verification into site and release gates

**Files:**
- Modify: `scripts/test-site-render.sh`
- Modify: `.github/workflows/pages.yml`
- Modify: 所有默认只假设单版本的 shell 或 Python 测试

- [ ] **Step 1: Extend render assertions**
为 `/fr`、`/fr/book`、本地化标签和 language-switch links 增加源码与输出断言。

- [ ] **Step 2: Make top-level site verification dual-edition**
确保站点测试命令在任一版本的 build、parity、figure 或 render 检查失败时整体失败。

- [ ] **Step 3: Promote the same contract to Pages**
更新 GitHub Pages 发布流程，使其在上传前运行同样的双版本校验链路。

- [ ] **Step 4: Final verification**
运行这个变更最小且完整的一组校验：双版本 `build:site`、双版本 parity checks、双版本 figure checks 与双版本 render assertions。
