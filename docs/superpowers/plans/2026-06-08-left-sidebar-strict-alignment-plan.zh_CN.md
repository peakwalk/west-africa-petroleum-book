# 左侧边栏严格对齐方案

> **面向代理式执行者：** 必须使用 `superpowers:executing-plans`（单一执行者时优先）或 `superpowers:subagent-driven-development`（如果要拆分 DOM/CSS/QA 工作流）按步骤实施本方案。

**目标：** 让桌面端左侧导航栏与已批准的 academic-reader 参考设计实现严格对齐，使其呈现为高品质专著级导航系统，而不是“被美化过的 mdBook 目录”，同时继续保持 mdBook 作为唯一内容与导航引擎。

**架构：** 保持 `theme/index.hbs` 作为唯一 shell 模板，继续从 mdBook / `SUMMARY.md` 获取导航，并在 `theme/custom.js` 中增加一个轻量的 **sidebar projection layer**，把 mdBook 注入的 TOC DOM 转换为设计对齐的左侧栏 section 与 row 组件。不要引入第二棵导航树、客户端框架或手工内容模型。

**技术栈：** mdBook、Handlebars 主题模板、CSS、原生 JavaScript、基于 shell 的渲染断言

---

## 问题陈述

当前左侧栏已经具备正确的高层结构：

1. 书籍身份信息块
2. 章节导航
3. 底部参考工具区

但它在真正影响观感质量的层面上仍然**没有**与参考设计对齐：

1. 左栏看起来像三个彼此割裂的区块，而不是一个统一的书籍导航仪表
2. 章节树仍然过于直接地暴露 mdBook TOC
3. 行级结构没有匹配参考设计中的“带编号的编辑式导航卡片”
4. 底部工具区域仍然更像普通链接，而不是参考设计里的 reference surfaces
5. 固定的顶部 / 中部 / 底部区域仍使用硬编码几何值，而不是从真实内容高度推导布局

---

## First Principles

1. **左侧栏是方位系统，不是原始索引。**
   - 它要回答的是：我在哪、我处于哪个章节簇、我可以跳到哪些相邻的参考界面。
2. **一条栏，一个网格。**
   - 引导区、导航区与工具页脚必须共享同一套水平节奏和 section 边界系统。
3. **导航行是组件，不是文本链接。**
   - 一个章节行必须明确拥有 ordinal、label、active state 和 multiline wrapping 这些槽位。
4. **固定区域必须推导出来，而不是猜。**
   - 如果顶部和底部区域是 sticky，中间可滚动区域就必须根据测得的高度来定尺寸，而不是依赖 magic numbers。
5. **mdBook 仍然是唯一真相来源。**
   - 左栏可以做变换、重组或附加标注，但数据仍然必须来自 mdBook 输出和 `SUMMARY.md`。

---

## MECE 根因分析

### 1. 几何契约不匹配

左侧栏从上到下没有共享一套稳定的几何契约。

- `book-sidebar-intro`、scrollbox 与 `book-sidebar-utilities` 使用了不同的视觉 padding 规则
- 中部可滚动区域仍依赖硬编码偏移：
  - `top: 6.35rem`
  - `bottom: 10.2rem`
- 这些值是针对旧字号体系调过的，现在已经与实际 intro/footer 内容高度脱节

**影响：** 即使文字尺寸改善了，左栏仍会略显压缩、间距失衡，或在视觉上前后不一致。

### 2. 导航结构投影不匹配

当前左栏仍然过于直接地在给 mdBook 的平面 TOC 做样式。

证据：

- mdBook 通过 `public/book/toc-*.js` 注入一个平面的 `<ol class="chapter">`
- `Front Matter`、`Part I`、`Part II`、`Part III`、`Back Matter` 都是以原始 `li.part-title` 节点进入页面
- 章节链接则作为 `.chapter-link-wrapper` 内的普通锚点出现

而参考设计**并不是**直接这样呈现原始结构。它投影成：

1. 顶部一个“Front Matter”导航组
2. 若干个清晰分隔的 part 区块
3. 带编号的章节行，并具有编辑级层次
4. 与正文导航视觉分离的工具页脚

**影响：** 当前样式也许可以改善排版，但只要 DOM 仍然像平面文档列表，就不可能达到严格保真。

### 3. 行组件结构不匹配

设计期望每个可导航章节项都表现为一个结构化行组件，但当前实现只是在样式化一个通用锚点。

当前约束：

- `.book-sidebar-shell .chapter li a` 只是一个带 padding 的单块链接，内部是内联文本

参考设计期望：

1. 独立的 ordinal lane
2. 独立的 text lane
3. 可预测的多行换行宽度
4. 蓝色 active card 与末端圆点要对齐卡片，而不是对齐原始文本
5. 对 `Cover`、`Glossary`、`Bibliographical References` 这类非章节项做不同处理

**影响：** 左栏缺失了那种清晰的“编号 + 标题”层次，因此它更像工具型目录，而不是编辑型导航。

### 4. 分区视觉语言不匹配

section 级别的视觉 affordance 仍然没有匹配参考设计。

- 顶部 “Front Matter” 区域没有作为明确的 rail group header 渲染，也没有自己的 section chrome
- part 标题仍然是信息量很低的原始 `part-title` 行
- 底部 `Reference Surfaces` 链接仍然是普通文本行；参考设计使用了更丰富的工具面板处理
- 当前 footer 缺少 icon slot，也缺少参考设计中更强的 “surface” 语义

**影响：** 即使排版修正了，左栏仍然读起来像“样式化 TOC + 额外链接”，而不是一个被设计过的导航对象。

### 5. 交互与状态模型不匹配

当前状态模型相对于设计需求仍然偏弱。

- 当前 active state 处理主要围绕 `a.active` 和 `a.current-header`
- 没有显式的 “current part block”、“front matter group” 或 “utility surface state” 概念
- 当前实现不会依据真实 DOM 条件推导 sticky 区域的测量值或 section 状态

**影响：** 某些地方的视觉上已经接近，但行为上仍然松散，因此并不是真正对齐。

### 6. 验证缺口

当前测试覆盖了：

1. sidebar 的存在
2. 宽度 token
3. 排版 token
4. 已删除产物的缺失

但它们还**没有**锁定：

1. 投影后的 sidebar section wrappers
2. 带编号章节行的结构
3. utility-link icon 契约
4. 测量高度布局变量
5. 章节页与 back-matter 页上的 current-page state

**影响：** 左栏可以退化回“原始 mdBook 样式”，却不会在 CI 中失败。

---

## 解决策略

### 总览

**不要**替换 mdBook 导航。应增加一个 **left-rail projection layer**，消费 mdBook 注入的 TOC DOM，并将其重新渲染为更严格的导航结构。

这样既保持了 mdBook 作为单一真相来源，又允许在 shell 层获得设计保真度。

### 核心设计决策

1. **测量，不猜测**
   - 用根据观测到的 intro/footer 高度设置的 CSS custom properties，替换硬编码的 scrollbox `top` / `bottom` 值。
2. **把导航投影为显式分组**
   - 将平面 mdBook TOC 转换为：
     - `front-matter`
     - 每个 `Part` 一个 block
     - `back-matter`
3. **把章节行拆成显式槽位**
   - 把 `Chapter N: Title` 解析成：
     - chapter number slot
     - title slot
4. **按语义类型区分行类名**
   - chapter rows
   - front/back matter rows
   - utility footer rows
5. **保留模板中的静态 footer utilities，但升级它们的组件处理方式**
   - 增加 icon slot，并统一 row anatomy
6. **不要重新引入只存在于 mock 中的 `Download PDF`**
   - 除非产品在单独任务中明确恢复真实 canonical PDF 合同

---

## MECE 工作流拆分

### Workstream 1. Sidebar Shell Geometry

负责左栏的物理布局。

- 推导 `--sidebar-intro-height`
- 推导 `--sidebar-utilities-height`
- 基于这些变量计算 scrollbox inset
- 统一左右 padding 与 section 边界节奏

### Workstream 2. Navigation Projection Layer

负责从原始 mdBook TOC 到设计对齐分组的转换。

- 读取 mdBook 注入的 `.chapter` 列表
- 按 `part-title` 边界分组
- 重建 front matter / parts / back matter 的 section wrappers
- 保留原始 href、active state 与 mdBook 作为真相来源的地位

### Workstream 3. Row Component System

负责章节行结构与 section header 结构。

- 为 `Chapter N` 提供独立编号槽位
- 为多行标题提供 title 槽位
- active state card + end-dot
- 对非章节项使用独立样式

### Workstream 4. Utility Surfaces Footer

负责底部 reference surface 的处理方式。

- 每个 utility row 具备 icon slot
- 更紧凑但仍具品质感的 footer 布局
- 在相关页面上体现 current-page highlighting

### Workstream 5. Verification And Visual QA

负责测试覆盖与验收标准。

- 扩展 `scripts/test-site-render.sh`
- 在代表性页面上验证生成输出
- 做浏览器 QA，关注左栏对齐，而不是只做 CSS grep

---

## Non-Goals

1. 不要手改 `public/`。
2. 不要替换 mdBook TOC 生成逻辑。
3. 不要引入第二份手工维护的导航 JSON。
4. 不要把本任务扩展到 header、hero 或 right rail 重设计。
5. 不要恢复虚假的 `Download PDF` CTA。

---

## 文件映射

- 修改：`theme/index.hbs`
  - 可选地增加投影后 sidebar 内容与 utility icons 的 wrapper hook
- 修改：`theme/custom.css`
  - 左栏几何、section wrappers、row anatomy、utility row system
- 修改：`theme/custom.js`
  - sidebar projection、测量逻辑、current-state 同步
- 修改：`scripts/test-site-render.sh`
  - 投影后 DOM、CSS hooks 与 utility/footer state 的合同断言

---

## Acceptance Surfaces

在以下生成页面上验证左栏：

1. `public/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html`
   - `Part I` 中存在 active chapter row
2. `public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html`
   - `Part II` 中存在 active chapter row
3. `public/book/chapters/glossary.html`
   - back-matter active state
4. `public/book/chapters/list-of-figures.html`
   - utility-surface page state

---

## 实施计划

### Task 1. 在测试中锁定 Left-Rail Contract

**文件：**
- 修改：`scripts/test-site-render.sh`

- [ ] 为投影后的 sidebar 结构新增失败断言，例如：
  - `.reader-sidebar-section`
  - `.reader-sidebar-section-header`
  - `.reader-sidebar-section-body`
  - `.reader-sidebar-row`
  - `.reader-sidebar-row-index`
  - `.reader-sidebar-row-title`
  - `.book-sidebar-utility-link-icon`
  - `--sidebar-intro-height`
  - `--sidebar-utilities-height`
- [ ] 增加针对代表性页面 active-state 类名的生成输出检查。
- [ ] 运行 `npm run test:site`，并确认新的 left-rail contract 确实先失败。

### Task 2. 用测量几何替换 Magic Sidebar Offsets

**文件：**
- 修改：`theme/custom.css`
- 修改：`theme/custom.js`

- [ ] 添加 intro/footer 的 CSS 测量变量。
- [ ] 用这些变量替换硬编码的 scrollbox `top` / `bottom`。
- [ ] 在 `theme/custom.js` 中使用 `ResizeObserver` 保持这些变量同步。
- [ ] 保留现有移动端行为。

### Task 3. 基于 mdBook TOC 构建 Sidebar Projection Layer

**文件：**
- 修改：`theme/custom.js`

- [ ] 在 `mdbook-sidebar-scrollbox` 填充完成后读取注入的 `.chapter` 树。
- [ ] 解析 `part-title` 边界。
- [ ] 将条目分组为：
  - front matter
  - 每个 part 一个 section
  - back matter
- [ ] 重新渲染这些分组为显式 wrapper，同时保留原始 link target 和 active state。
- [ ] 确保 sidebar 发生 mutation 后，投影逻辑能够安全地重新执行。

### Task 4. 把章节行重建为结构化组件

**文件：**
- 修改：`theme/custom.css`
- 修改：`theme/custom.js`

- [ ] 将 `Chapter N: Title` 解析为 index + title 两个槽位。
- [ ] 将带编号的行渲染为双列导航组件。
- [ ] 将非编号项渲染为更简单的变体。
- [ ] 调整 active、hover、current-part 以及 multiline wrapping 行为，使其与参考设计对齐。

### Task 5. 升级 Front Matter / Part Headers / Back Matter 的视觉语言

**文件：**
- 修改：`theme/custom.css`
- 修改：`theme/custom.js`

- [ ] 为 `Front Matter` section 提供显式的 section-header 处理。
- [ ] 为每个 part block 提供更强的分隔与强调。
- [ ] 保持 `Back Matter` 更安静，但仍然成组。
- [ ] 确保各组之间的间距节奏与参考设计一致。

### Task 6. 升级 Reference Surfaces Footer

**文件：**
- 修改：`theme/index.hbs`
- 修改：`theme/custom.css`

- [ ] 为 footer utility links 增加 icon slot。
- [ ] 让 utility rows 与 chapter rows 处于同一左栏网格。
- [ ] 为 `Glossary`、`List of Figures` 等 utility 页面增加 current-page state。
- [ ] 不要增加 `Download PDF`。

### Task 7. 验证

**文件：**
- 修改：`scripts/test-site-render.sh`

- [ ] 运行 `npm run build:site`
- [ ] 运行 `npm run test:site`
- [ ] 对以上四个 acceptance surfaces 做浏览器 QA。
- [ ] 验证：
  - intro/footer 不会与 scrollbox 重叠
  - 当前 section 在视觉上足够明确
  - 行编号与标题对齐一致
  - utility footer 看起来像 reference surfaces，而不是孤立链接

---

## 预期终态

当本方案完成后，左栏应当：

1. 像一个统一设计过的导航仪表
2. 继续保持 mdBook 作为唯一导航引擎
3. 在 section 节奏、row anatomy 与 footer 处理上与参考设计视觉对齐
4. 不再依赖脆弱的硬编码偏移
5. 通过显式测试防止回归
