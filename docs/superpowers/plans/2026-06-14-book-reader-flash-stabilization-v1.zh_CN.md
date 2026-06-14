# Book Reader Flash Stabilization V1 Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在本次发布中不改变 reader 滚动模型的前提下，消除从左侧导航跳转时可见的布局闪动。

**Architecture:** 暂时保留当前 `#mdbook-reader-scroll` 行为，但停止在首屏后重建侧栏结构。增加一个仓库自有的 post-build 步骤，读取 `public/book/toc.html`，把最终 `.reader-sidebar-projection` 标记注入到生成的章节页中，并让 `theme/custom.js` 只保留非结构性的 reader 增强逻辑。通过在启动阶段门控布局类 transition，保证首屏视觉稳定。

**Tech Stack:** mdBook、Handlebars、vanilla JavaScript、Node.js 构建脚本、CSS、基于 shell 的渲染断言

---

**Scope Decision**

这个 `v1` 计划刻意比更大的静态布局路线图更窄。

纳入 `v1` 的内容：

- 启动阶段布局 transition 门控
- 构建期静态 sidebar 注入
- 删除 runtime sidebar reprojection
- 为新的启动契约补齐渲染测试覆盖

明确延期到 `v1` 之后的内容：

- 移除 `installInternalScrollerBridge()`
- 把页面切回浏览器原生 document scrolling
- 为新的 scroll root 重写 hash-scroll、progress 或 outline 逻辑

这个延迟就是主要的风险收敛点。最高风险面来自滚动模型，所以 `v1` 不碰它。

---

**File Map**

- `theme/index.hbs`：负责侧栏外壳标记以及任何 inline 的启动期 sidebar 逻辑。
- `theme/custom.js`：负责运行时 reader 增强；在 `v1` 中它必须停止在首屏后重建侧栏结构。
- `theme/custom.css`：负责布局 transition 行为和首屏 motion 契约。
- `scripts/build_static_reader_sidebar.mjs`：新的构建步骤，把 `public/book/toc.html` 转成注入式最终 sidebar 标记。
- `package.json`：把新的构建步骤接入 `build:site`。
- `scripts/preview.sh`：把新的构建步骤接入 preview build。
- `scripts/test-site-render.sh`：负责新的静态侧栏和启动稳定性契约的回归断言。

### Task 1: Stop The Visible Flash First

**Files:**
- Modify: `theme/index.hbs`
- Modify: `theme/custom.css`
- Modify: `scripts/test-site-render.sh`

- [ ] **Step 1: Add a boot-state contract for reader layout**

在模板渲染时增加一个只用于启动阶段的 class 或 attribute，让布局类 transition 可以在页面 ready 前被禁用。

- [ ] **Step 2: Gate layout-affecting transitions behind that boot-state contract**

更新 `theme/custom.css`，确保 `padding-inline-start`、`width`、`margin-inline-start` 这类影响几何布局的 motion 在初始页面加载时不执行动画。

- [ ] **Step 3: Remove one of the two sidebar startup paths before structural refactoring**

在静态侧栏步骤落地前，先临时只保留一条启动路径，避免 rail 在首屏前后被可见地绘制两次。

- [ ] **Step 4: Lock the contract in render assertions**

更新 `scripts/test-site-render.sh`，一旦启动门控消失或重新引入无条件的布局 transition，就让测试失败。

### Task 2: Inject Static Sidebar Markup At Build Time

**Files:**
- Create: `scripts/build_static_reader_sidebar.mjs`
- Modify: `package.json`
- Modify: `scripts/preview.sh`
- Modify: `scripts/test-site-render.sh`

- [ ] **Step 1: Parse the generated mdBook sidebar source**

读取 `public/book/toc.html`，提取 `<ol class="chapter">` 结构，并把行分组为：

- `front-matter`
- `part` sections
- `back-matter`

- [ ] **Step 2: Render final `.reader-sidebar-projection` markup in Node**

在 Node 构建步骤里生成与当前 runtime projection 相同语义的 sidebar 结构，让最终侧栏在浏览器首屏前就已经存在。

- [ ] **Step 3: Inject the rendered sidebar into generated book pages**

把最终 projection 标记写入：

- `public/book/index.html`
- `public/book/chapters/*.html`

并在注入时按页面路径标记正确的 active row。

- [ ] **Step 4: Wire the script into both release and preview builds**

把新脚本接入：

- `npm run build:site`
- `scripts/preview.sh`

preview 路径和 release 路径必须保持一致。

- [ ] **Step 5: Add render assertions for the new static injection**

更新 `scripts/test-site-render.sh`，断言生成后的章节页在不依赖 runtime JS 的前提下，已经包含最终 sidebar projection 和 active-state 标记。

### Task 3: Remove Runtime Sidebar Reprojection Only

**Files:**
- Modify: `theme/index.hbs`
- Modify: `theme/custom.js`
- Modify: `scripts/test-site-render.sh`

- [ ] **Step 1: Delete the inline sidebar projection bootstrap from the template**

在静态注入就位后，从 `theme/index.hbs` 删除 inline 的 `bootstrapSidebarProjection()` 路径。

- [ ] **Step 2: Delete `installSidebarProjection()` and related helpers from `theme/custom.js`**

删除 `theme/custom.js` 中那些在 `DOMContentLoaded` 之后重建 sidebar row、重新分组 part、或再次执行 sidebar projection 的 runtime 代码。

- [ ] **Step 3: Remove runtime offset restoration that depends on reprojection geometry**

如果 `sessionStorage` 偏移恢复仍依赖 runtime projection 期间计算出来的行几何，就把这段会在首屏后改 rail 的逻辑删掉。

- [ ] **Step 4: Keep the existing scroll bridge unchanged in `v1`**

本次不要修改：

- `installInternalScrollerBridge()`
- `document.scrollingElement` overrides
- hash scrolling bridge
- 绑定当前 scroller 的 progress 计算

这是一个显式的“不变更项”，应当视为验收标准的一部分。

- [ ] **Step 5: Add negative assertions so reprojection does not come back**

更新 `scripts/test-site-render.sh`，一旦 `theme/custom.js` 或 `theme/index.hbs` 重新引入被删除的 sidebar projection bootstrap 代码，就让测试失败。

### Task 4: Verify The Narrow Contract

**Files:**
- Test: `scripts/test-site-render.sh`
- Test: `scripts/test-preview-build.sh`

- [ ] **Step 1: Run the source and generated-output assertions**

Run: `npm run test:site`

Expected: PASS.

- [ ] **Step 2: Run the preview build path**

Run: `sh scripts/test-preview-build.sh`

Expected: PASS.

- [ ] **Step 3: Perform manual navigation smoke checks**

至少验证：

- `foreword.html -> chapter-01`
- `chapter-01 -> chapter-02`
- `chapter-04 -> chapter-05`
- `general-conclusion -> glossary`

Expected:

- 没有可见页面闪动
- 首屏即有正确 active row
- 没有延迟发生的 sidebar reprojection
- 当前 scroll 相关行为无回归

---

## Acceptance Criteria

只有当以下条件全部成立时，`v1` 才算完成：

1. 从左侧导航进行页面跳转时，不再出现可见的位移 / 闪动
2. 生成后的章节 HTML 在客户端 JS 运行前就包含最终 sidebar projection 标记
3. `theme/index.hbs` 不再包含 inline sidebar projection bootstrap
4. `theme/custom.js` 不再包含 runtime sidebar reprojection
5. 现有 scroll bridge 行为与之前完全一致
6. `npm run test:site` 和 `sh scripts/test-preview-build.sh` 都通过

---

## Risks And Why This Plan Is Safer

### Reduced Risk 1: No scroll-root migration

本方案不改 reader 现有的滚动模型，因此避开了以下高概率回归：

- hash navigation
- progress tracking
- outline state sync
- sticky menu behavior

### Reduced Risk 2: One structural change at a time

`v1` 唯一的结构性迁移，就是把 sidebar projection 从 runtime 挪到 build time。

### Remaining Risk: Active-row injection mismatch

构建期注入需要把页面路径映射成与之前 runtime sidebar 一致的 active state。

缓解方式：

- 对生成 HTML 中的 active marker 做断言
- 对 front matter、chapter、back matter 代表性页面做 smoke test

---

## Follow-Up After V1

如果 `v1` 能干净地移除闪动，下一份计划再单独评估是否还值得移除 internal scroll bridge。

这个后续应该被视为另一个 change，而不是被悄悄混入本次执行中。
