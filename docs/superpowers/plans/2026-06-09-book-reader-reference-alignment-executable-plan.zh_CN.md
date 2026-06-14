# /book Reader Reference Alignment 可执行实施计划

> **面向代理式执行者：** 必须使用 `superpowers:executing-plans`（单一执行者优先）或 `superpowers:subagent-driven-development`（如果明确拆分 DOM/CSS/QA 工作流）按步骤实施本方案。步骤使用 checkbox（`- [ ]`）语法跟踪。

**Goal:** 在不替换 mdBook、不手改 `public/`、不改 landing page 的前提下，把 `/book` reader surface 从“精修过的 mdBook 页面”推进到“与批准参考稿同一视觉系统的学术阅读器”，重点收敛 `wide-reference.png` 与 `narrow-reference.png` 在 shell、导航、hero、figure/table/formula 和 responsive 语义上的差异。

**Architecture:** 保持 mdBook 为唯一内容与导航引擎。`theme/index.hbs` 负责 reader shell 骨架，`theme/custom.css` 负责 repo-owned reader token 与组件视觉合同，`theme/custom.js` 负责把 mdBook 原始 DOM 投影成设计对齐的 left rail / outline / hero / knowledge object chrome。不得新增第二套手工目录数据源，不得通过修改 `public/` 伪造结果。

**Tech Stack:** mdBook, Handlebars theme template, CSS, vanilla JavaScript, shell-based render assertions, browser QA

---

## 结论

当前与参考稿视觉差异大的根因，不是单个字号、背景色或 root font size，而是：

1. 现在的 `/book` 仍然主要表现为 **mdBook 内容页 + 视觉覆盖**
2. 参考稿表达的是一套 **完整的 academic reader 产品壳层**
3. 两者差异同时存在于：
   - 信息结构
   - 组件边界
   - 视觉合同
   - 运行时投影
   - 浏览器级验收

因此，正确策略不是继续局部调 CSS，而是把 `/book` 的 reader shell 当成仓库自有产品层进行对齐实施。

---

## Problem Statement

当前实现已经完成了 `/book` root font contract 显式化，但仍未达到参考稿要求的核心原因有五类：

1. 左栏仍然过度暴露 mdBook TOC 的原始形态
2. 右栏仍然更像普通页内目录，而不是阅读辅助 rail
3. chapter hero 仍然是“正文前插入块”，不是参考稿级入口组件
4. figure / table / formula 已有局部风格，但还未完全组成统一的知识对象系统
5. 当前测试更多保护 source/build contract，未形成浏览器级 reference acceptance contract

---

## First Principles

1. **阅读优先于生成器兼容性。**
   - `mdBook` 是内容与导航引擎，不是视觉设计系统。只要不破坏内容来源与导航事实，就应优先让 reader 更可读、更易定位。

2. **reader shell 必须由仓库自己拥有。**
   - header、left rail、outline rail、hero、figure/table/formula、pagination 都必须以 repo-owned contract 为源头，而不是从 mdBook 默认视觉“推断”。

3. **设计稿的价值在于视觉与层级合同，不在于逐字照抄 mock 文案。**
   - live 章节标题、目录项、figure/table 数量可以不同，但 shell、层级、状态语法和知识对象语言必须一致。

4. **响应式是折叠，不是换皮。**
   - 窄屏是同一 reader 的语义压缩版，不应变成另一套产品。

5. **视觉一致性必须经过浏览器级验证。**
   - source grep 与构建通过只说明“代码存在”，不能说明“视觉接近参考稿”。

---

## MECE Root Cause Analysis

### 1. Shell Product Mismatch

当前 `/book` 仍以 mdBook 页面形态为主，再覆盖 reader 样式；参考稿则是明确的产品壳层。

**Effect:** 用户看到的是“带导航的文档页”，不是“学术阅读器”。

### 2. Navigation Projection Mismatch

左栏和右栏都仍然过于忠实地暴露原始 mdBook DOM。

- 左栏更像 TOC 样式化
- 右栏更像 heading list
- reference surfaces 与 knowledge-object rail 语法不统一

**Effect:** 结构对了，但气质不对。

### 3. Component Boundary Mismatch

当前 hero、sidebar row、outline item、table header、formula panel 等很多对象，仍然是“在已有 HTML 上叠样式”，而不是边界清晰的 reader 组件。

**Effect:** 单点修正会互相牵连，难以持续逼近参考稿。

### 4. Visual Contract Coverage Gap

虽然 root contract 与部分 token 已显式化，但参考稿中的很多视觉决定还没有变成受保护的 reader token / component contract，例如：

- left rail 背景语言
- hero 入口权重
- outline reference 区块语法
- pagination 的版式叙事感
- utility/footer surfaces 的完整呈现

**Effect:** 视觉系统不完整，结果看起来像多套风格拼起来。

### 5. Verification Gap

当前 CI 主要保护 source 与 build 合同，缺少 reference-oriented browser QA。

**Effect:** 即使测试通过，依然可能和参考稿差很大。

---

## Recommended Decision

### Decision

进入第二阶段 `/book` reader 对齐工程：

**不再把问题定义成 token 微调，而是对 reader shell 做一次受控的 reference alignment 重构。**

### Why This Is The Right Decision

1. 它延续了已经完成的 root contract 显式化成果
2. 它不破坏 mdBook 的内容与导航引擎角色
3. 它能把“局部好看”升级为“整体一致”
4. 它能让后续迭代继续建立在仓库自有组件系统上，而不是继续追着 legacy selector 打补丁

### What This Decision Is Not

- 不是切换到 React/Vue 客户端壳层
- 不是替换 mdBook
- 不是直接照抄 mock 文案
- 不是只调左栏背景或字号
- 不是 landing page 改版

---

## Scope

### In Scope

- `/book` reader shell 宽屏与窄屏 reference alignment
- left rail 结构与 row anatomy
- right rail / on-this-page / figures / tables projection
- chapter hero 组件
- figure / table / formula 统一视觉语言
- pagination chrome
- `/book` 相关测试与浏览器级验收

### Out Of Scope

- landing page 视觉系统改版
- `public/` 手工编辑
- `SUMMARY.md` 内容结构重写
- mdBook 内容引擎替换
- 新增客户端框架
- 伪造 mock-only 内容对象

---

## Non-Goals

1. 不恢复 `Reference Surfaces` 这个已移除的信息架构名词
2. 不新增第二份人工维护的导航 JSON
3. 不为了贴 mock 而篡改真实章节标题或正文顺序
4. 不把左栏对齐任务扩散成全站 marketing shell 改造
5. 不在没有真实 canonical 来源的前提下恢复假 `Download PDF`

---

## Source Reality vs. Reference Reality

参考稿表达的是一套阅读器设计语言，不是对 live book 的逐字逐结构截图。

因此实施原则必须是：

1. **shell 与组件 treatment 以参考稿为真**
2. **内容与导航事实以 mdBook live 输出为真**
3. **当两者冲突时，保持 live 内容事实，投影参考稿组件语言**

这意味着：

- chapter 标题可以不是 mock 里的标题
- left rail 的条目数量可以不同
- right rail 中 figures/tables 的数量可以不同
- 但品牌、层级、节奏、卡片语法、状态表现、知识对象语言必须对齐

---

## File Map

- `theme/index.hbs`
  - reader shell 骨架
  - sidebar / toolbar / main / outline 的静态 slots
  - 只能保留一份 reader shell template

- `theme/custom.css`
  - repo-owned root contract
  - reader token layer
  - component styling
  - responsive transformation rules
  - legacy compatibility shrink-wrap

- `theme/custom.js`
  - sidebar projection
  - outline projection
  - hero injection / normalization
  - figure / table / formula enhancement glue
  - current-page state sync

- `scripts/test-site-render.sh`
  - source contract assertions
  - generated HTML assertions
  - reader token / projection / surface assertions

- Acceptance surfaces
  - `public/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html`
  - `public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html`
  - `public/book/chapters/glossary.html`
  - `public/book/chapters/bibliographical-references.html`
  - `public/book/index.html`

---

## Acceptance Contract

最终结果必须同时满足五层合同：

### 1. Engine Contract

- mdBook 仍是唯一内容与导航引擎
- 不手改 `public/`
- canonical nav 结构不变

### 2. Shell Contract

- header、left rail、main、right rail、pagination 组成统一 reader shell
- 宽窄屏是同一产品，只做折叠与密度变化

### 3. Component Contract

- hero、sidebar row、outline item、figure、table、formula 属于同一视觉系统
- `General Conclusion`、`Glossary`、`Bibliographical References` 在 mdBook projection 中保留 icon treatment

### 4. Token Contract

- reader 关键视觉来源于 repo-owned `--reader-*`
- 不再依赖 mdBook 默认视觉推断

### 5. Verification Contract

- `npm run test:site`
- `npm run build:site`
- 浏览器 QA 完成并记录观察

---

## Migration Strategy

### Phase 1. Freeze The Reader Boundary

先明确：

1. 什么属于 mdBook engine DOM
2. 什么属于 reader presentation DOM
3. 哪些 legacy selector 仅作兼容，不再作为主实现路径

**Outcome:** 后续不再继续无边界打补丁。

### Phase 2. Rebuild Reader Shell Tokens

把 shell、navigation、hero、knowledge object 的关键值完整映射到 repo-owned token。

**Outcome:** 视觉来源统一。

### Phase 3. Rebuild Navigation Projection

把左栏和右栏都视为 reader projection，而不是原始 TOC 的样式化。

**Outcome:** 结构与气质开始逼近参考稿。

### Phase 4. Rebuild Hero And Knowledge Objects

把 hero / figure / table / formula 做成统一组件系统。

**Outcome:** 正文入口与知识对象语言统一。

### Phase 5. Lock Browser Acceptance

把最终视觉收敛建立在浏览器级验收之上，而不是继续只靠 CSS grep。

**Outcome:** 以后不会反复回退到“看起来又不像”。

---

## MECE Workstreams

### Workstream 1. Reader Shell And Brand

负责：

- header brand lockup
- search/contact balance
- shell background / rails / pagination shell

### Workstream 2. Navigation And Orientation

负责：

- desktop left rail
- desktop right rail
- mobile chapter bar
- mobile inline outline

### Workstream 3. Chapter Entry Experience

负责：

- eyebrow
- hero title
- rule
- meta
- dek

### Workstream 4. Knowledge Object System

负责：

- formula panels
- figure cards
- table shells
- captions / labels / notes

### Workstream 5. Verification And QA

负责：

- source/build assertions
- generated surface assertions
- browser QA
- visual delta closure

---

## TDD And Execution Order

### 总原则

每个阶段都遵守：

1. 先写或改测试，让旧实现先失败
2. 再改实现
3. 再跑 build 与 QA

### 执行顺序

1. reader shell token contract
2. left rail projection
3. right rail projection
4. chapter hero
5. figure / table / formula
6. responsive collapse behavior
7. browser QA

原因：

- left rail / right rail 是当前视觉差异最大的结构面
- hero 与 knowledge objects 要建立在稳定 shell 之后
- responsive 必须最后统一收敛，避免中途重复推翻

---

## Detailed Implementation Plan

### Task 1. 锁定 reference alignment 的测试合同

**Files:**
- Modify: `scripts/test-site-render.sh`

- [ ] Step 1: 把现有 `/book` 测试分成四类断言
  - token contract
  - projection contract
  - shell contract
  - knowledge object contract

- [ ] Step 2: 为 left rail 增加失败断言
  - section wrappers
  - row anatomy
  - active state card
  - icon treatment
  - utility/footer treatment

- [ ] Step 3: 为 right rail 增加失败断言
  - figures/tables sections
  - concise reference label strategy
  - active marker contract

- [ ] Step 4: 为 hero 增加失败断言
  - eyebrow
  - title scale
  - rule
  - meta
  - dek

- [ ] Step 5: 为 figure/table/formula 增加失败断言
  - card shell
  - caption grammar
  - table header
  - formula grouped panel consistency

- [ ] Step 6: 运行 `npm run test:site`
  - Expected: FAIL，证明 reference alignment contract 已经被锁住

---

### Task 2. 抽离完整 reader token 层

**Files:**
- Modify: `theme/custom.css`

- [ ] Step 1: 把 reader token 分为：
  - semantic
  - layout
  - sidebar
  - outline
  - hero
  - figure
  - table
  - formula
  - pagination

- [ ] Step 2: 停止在主组件 block 里继续散写可复用尺寸

- [ ] Step 3: 为参考稿未覆盖但实现需要的过渡值建立清晰命名，而不是继续使用匿名魔法数

- [ ] Step 4: 运行 `npm run test:site`
  - Expected: 仍 FAIL，但失败点转移到 projection / component 层

---

### Task 3. 重做 desktop left rail projection

**Files:**
- Modify: `theme/custom.js`
- Modify: `theme/custom.css`
- Potentially modify: `theme/index.hbs`（仅在需要额外 projection slot 时）

- [ ] Step 1: 把左栏投影层拆成显式模块
  - `buildSidebarProjectionData`
  - `renderSidebarSection`
  - `renderSidebarRow`
  - `syncSidebarActiveState`

- [ ] Step 2: 前言、Part、Back Matter 分组由 projection 层统一生成，不再让 raw TOC 直接决定最终视觉

- [ ] Step 3: chapter row 固定为 slot 语法
  - ordinal lane
  - title lane
  - active end-dot

- [ ] Step 4: 保留真实 href 与 active state，不引入第二套导航事实源

- [ ] Step 5: 让底部 utility rows 与正文章节 row 形成清晰但同体系的区别

- [ ] Step 6: 保留 `General Conclusion`、`Glossary`、`Bibliographical References` icon treatment

- [ ] Step 7: 运行 `npm run test:site`
  - Expected: left rail 相关断言转绿

---

### Task 4. 重做 desktop right rail projection

**Files:**
- Modify: `theme/custom.js`
- Modify: `theme/custom.css`
- Potentially modify: `theme/index.hbs`

- [ ] Step 1: 统一 heading / figures / tables 在右栏的 section grammar

- [ ] Step 2: 将 figure/table reference text 改为受控的短标签策略
  - 不直接倾倒完整 caption prose

- [ ] Step 3: 统一 label、section title、item、active marker 的视觉合同

- [ ] Step 4: 让右栏保留 quiet assistive rail 的气质，而不是索引墙

- [ ] Step 5: 运行 `npm run test:site`
  - Expected: right rail 相关断言转绿

---

### Task 5. 重做 chapter hero

**Files:**
- Modify: `theme/custom.js`
- Modify: `theme/custom.css`

- [ ] Step 1: 明确 hero 只作用于 chapter pages，不污染 cover / aux pages

- [ ] Step 2: 统一 eyebrow / title / rule / meta / dek 的布局和文本策略

- [ ] Step 3: 限制 hero 文本 measure 与换行，避免 live 长标题把版面压坏

- [ ] Step 4: 调整 meta 语法，使其看起来像 reader metadata，而不是标签集合

- [ ] Step 5: 运行 `npm run test:site`
  - Expected: hero 相关断言转绿

---

### Task 6. 统一 figure / table / formula 组件系统

**Files:**
- Modify: `theme/custom.css`
- Modify: `theme/custom.js`（仅当需要统一包装或注入辅助容器时）

- [ ] Step 1: figure card 统一 shell / media / caption / label

- [ ] Step 2: table shell 统一 header / caption / notes / overflow

- [ ] Step 3: grouped formula、single formula、table-cell formula 保持同一语言

- [ ] Step 4: 检查 figure/table/formula 在宽窄屏是否只是布局折叠，而不是换皮

- [ ] Step 5: 运行 `npm run test:site`
  - Expected: knowledge object 相关断言全部转绿

---

### Task 7. 收敛 responsive shell

**Files:**
- Modify: `theme/custom.css`
- Modify: `theme/custom.js`

- [ ] Step 1: desktop / tablet / phone 三档断点规则统一整理

- [ ] Step 2: chapter bar / drawer / inline outline card 共享同一 reader 语言

- [ ] Step 3: 确保窄屏保留完整横向 logo lockup，`compact logo` 只作 fallback

- [ ] Step 4: 收紧移动端密度，但不破坏知识对象一致性

- [ ] Step 5: 运行 `npm run test:site`
  - Expected: responsive contract 转绿

---

### Task 8. 构建与浏览器验收

**Files:**
- No source change required unless QA 暴露新问题

- [ ] Step 1: 运行 `npm run test:site`
- [ ] Step 2: 运行 `npm run build:site`
- [ ] Step 3: 如果环境允许，针对以下页面做 browser QA
  - `public/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html`
  - `public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html`
  - `public/book/chapters/glossary.html`
  - `public/book/chapters/bibliographical-references.html`
  - `public/book/index.html`

- [ ] Step 4: 记录每个 acceptance surface 的观察
  - left rail background
  - left rail density
  - hero scale
  - right rail quietness
  - figure/table/formula weight

- [ ] Step 5: 只修 QA 暴露的真实偏差，不顺手做无关重构

---

## Browser QA Checklist

### Wide

- [ ] 左栏背景、边界、section 节奏接近参考稿
- [ ] active chapter row 视觉重量正确
- [ ] 中间正文第一屏先建立阅读上下文，再进入正文
- [ ] 右栏不是信息噪音墙
- [ ] figure/table/formula 同属一套 publication language

### Narrow

- [ ] header 保留完整 logo lockup
- [ ] chapter bar 提供当前章节语义
- [ ] drawer 与 desktop left rail 是同一系统
- [ ] inline outline card 可读
- [ ] 图表公式只折叠，不换皮

---

## Risks

1. **live 内容比参考稿更长**
   - 需要靠 measure、truncate、slot layout 控制，而不是硬压字号。

2. **mdBook 原始 DOM 变化可能影响 projection**
   - 必须把 projection contract 写进测试，而不是只相信当前 DOM 形状。

3. **right rail 容易再次变成过密索引**
   - 必须优先控制 reference 文本长度与 section 数量感。

4. **responsive 收敛容易误伤桌面**
   - 必须最后统一 breakpoint，而不是中途反复打补丁。

5. **浏览器 QA 如果缺失，视觉偏差会漏过**
   - 必须把浏览器 QA 当成正式 acceptance，而不是可选项。

---

## Done Definition

只有同时满足以下条件，任务才算完成：

1. `/book` 仍由 mdBook 驱动
2. `public/` 未手工编辑
3. left rail / right rail / hero / figure / table / formula 与参考稿属于同一视觉系统
4. `General Conclusion`、`Glossary`、`Bibliographical References` icon treatment 保留
5. `npm run test:site` 通过
6. `npm run build:site` 通过
7. 浏览器 QA 已完成并记录观察

---

## 建议执行方式

如果下一步直接实施，建议按如下顺序开工：

1. `scripts/test-site-render.sh`
2. `theme/custom.css` token layer
3. `theme/custom.js` sidebar projection
4. `theme/custom.js` outline projection
5. `theme/custom.js` hero
6. `theme/custom.css` knowledge object system
7. responsive 收敛
8. browser QA

这能保证每一步都有明确失败点，不会再次回到“看起来不像，但说不清为什么”的状态。
