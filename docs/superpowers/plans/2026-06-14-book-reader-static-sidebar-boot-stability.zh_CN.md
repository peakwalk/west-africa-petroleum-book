# Book Reader 静态侧栏与首屏稳定性方案

> **面向代理式执行者：** 必须使用 `superpowers:executing-plans`（单人执行时优先）或 `superpowers:subagent-driven-development`（如果要拆分构建 / 运行时 / QA 工作流）按步骤实施本方案。

**目标：** 通过把 reader 首屏布局从“晚到的 JavaScript 改写”迁回“构建期 HTML/CSS”，消除从左侧导航跳转时的页面闪动，同时继续保持 mdBook 作为导航真相来源。

**架构：** 保持 mdBook 继续生成规范 TOC 和章节 HTML，再增加一个仓库自有的 post-build 步骤，读取 `public/book/toc.html`，渲染出最终的 reader sidebar 标记，并在 preview / test / release 验证之前注入到生成的章节页中。把 `theme/custom.js` 收缩为渐进增强层；它不再在首屏后重建侧栏结构、重写 scroll root 或改变页面几何布局。

**技术栈：** mdBook、Handlebars 主题模板、原生 JavaScript、Node.js 构建脚本、CSS、基于 shell 的渲染断言

---

## 决策摘要

这次改造**不应该**被实现为一次泛化的“去掉所有 JS”工程。

它应该被实现为一次 **首屏契约清理**：

1. 侧栏 DOM 必须以最终形态存在于生成 HTML 中
2. 浏览器必须保留原生 document scroll 模型
3. 运行时 JS 可以做增强，但不能在首屏后重建导航结构或改写滚动语义
4. 布局类 transition 不得在启动阶段执行

这样可以拿到静态布局的稳定性收益，同时保留真正有价值的渐进增强能力。

---

## 为什么当前设计会闪

当前闪动来自三类职责都被塞进了运行时 JS：

1. `theme/index.hbs` 先内联执行了一次 sidebar projection
2. `theme/custom.js` 又在 `DOMContentLoaded -> requestAnimationFrame` 之后执行第二次 sidebar projection
3. `theme/custom.js` 还把 `document.scrollingElement`、`window.scrollY`、`window.scrollTo`、hash 跳转等桥接到了 `#mdbook-reader-scroll`

这会导致页面先按浏览器默认文档布局被绘制一次，之后再因为 rail 和 scroll model 被 JS 改写而被校正一次。

这个可见效果又被 `theme/custom.css` 里的布局类 transition 放大了，特别是：

- `.reader-main { transition: padding-inline-start 180ms ease; }`
- `.book-progress { transition: width 180ms ease, margin-inline-start 180ms ease; }`

---

## 第一性原理下的目标状态

重构完成后，reader 应遵守以下原则：

1. **一棵导航树**
   - mdBook 仍然是唯一真相来源
   - 生成页面直接包含最终渲染好的 reader sidebar，而不是一个等待 JS 重建的占位结构

2. **一个 scroll root**
   - 浏览器文档自身仍然是 scroll root
   - 不在运行时覆盖 `document.scrollingElement`、`window.scrollY`、`window.scrollTo`、`window.scrollBy`

3. **首屏零几何改写**
   - 不再做 sidebar projection 重建
   - 不再做首屏后改变几何位置的 rail scroll 校正
   - 启动阶段不执行布局类 transition

4. **JS 只做增强**
   - 搜索、outline、轻量状态同步等能力可以保留在 JS 中
   - 首屏结构和几何布局不能依赖 JS 才成立

---

## 文件映射

### 新增

- `scripts/build_static_reader_sidebar.mjs`

### 修改

- `package.json`
- `scripts/preview.sh`
- `scripts/test-site-render.sh`
- `theme/index.hbs`
- `theme/custom.js`
- `theme/custom.css`

### 实施时需要对照

- `public/book/toc.html`：当前构建产物中的规范 TOC 来源
- `scripts/build_reader_page_meta.mjs`：可复用的 build-step 风格与输出路径约定
- `scripts/strip_mdbook_onunload.mjs`：现有 mdBook 后处理脚本在构建链中的插入位置

---

## 实施阶段

### 阶段 0：先加稳定性护栏，再做结构改造

**目的：** 先把当前可见闪动压下去，为后续结构重构腾出空间。

**文件：**

- 修改：`theme/index.hbs`
- 修改：`theme/custom.css`
- 修改：`scripts/test-site-render.sh`

**改动：**

1. 增加一个启动态 class，例如 `book-layout-booting`
2. 在该 class 存在时屏蔽几何布局相关 transition
3. 在深入重构前先移除两条 sidebar projection 启动路径中的一条
4. 新增渲染断言，确保几何 transition 只在 boot-ready 之后启用，而不是首屏即启用

**验收：**

- 左侧导航在启动阶段不再出现两次可见绘制
- 一旦有人重新引入“无启动门控的布局 transition”，`scripts/test-site-render.sh` 会失败

**为什么要单独拆出这一阶段：**

这是对当前症状风险最低的修复，即使完整的静态侧栏迁移需要更久，也可以先独立上线。

---

### 阶段 1：构建期静态侧栏注入

**目的：** 把侧栏结构生成从运行时 JS 挪到构建管线。

**文件：**

- 新增：`scripts/build_static_reader_sidebar.mjs`
- 修改：`package.json`
- 修改：`scripts/preview.sh`
- 修改：`scripts/test-site-render.sh`

**改动：**

1. 读取 `public/book/toc.html`
2. 把生成的 `<ol class="chapter">` 解析为语义分组：
   - `front-matter`
   - 每个 `Part` 一个 section
   - `back-matter`
3. 根据该结构渲染最终 sidebar projection HTML
4. 把渲染结果注入到：
   - `public/book/index.html`
   - `public/book/chapters/*.html`
5. 在注入阶段基于目标页面路径标记 active row
6. 如果过渡期还需要 `mdbook-sidebar-scrollbox`，只把它保留为兼容性后备；最终目标是 projected markup 成为主要可见结构
7. 把新脚本同时接入：
   - `npm run build:site`
   - `scripts/preview.sh`

**推荐实现细节：**

不要为了这一步引入新的 DOM 解析依赖。`toc.html` 的生成格式简单、受控，而且今天已经在间接依赖它。优先使用仓库内的纯 Node 解析逻辑，不要为此引入 `cheerio` 或客户端框架。

**验收：**

- 在客户端 JS 运行之前，生成的章节 HTML 已经包含最终 `.reader-sidebar-projection`
- active page 高亮直接存在于生成 HTML 中
- preview 和 release build 走同一条注入路径

---

### 阶段 2：删除运行时侧栏二次投影

**目的：** 删除首屏后重建侧栏结构的那条代码路径。

**文件：**

- 修改：`theme/index.hbs`
- 修改：`theme/custom.js`
- 修改：`scripts/test-site-render.sh`

**改动：**

1. 从 `theme/index.hbs` 删除内联的 `bootstrapSidebarProjection()` 代码块
2. 从 `theme/custom.js` 删除 `installSidebarProjection()` 及其辅助函数
3. 删除 sidebar DOM 变动后再次执行 projection 的 mutation observer 行为
4. 删除依赖运行时重投影行几何的 sessionStorage 偏移恢复逻辑
5. 只保留在静态注入之后仍然有明确价值的最小 sidebar JS

**重要产品决策：**

如果要保留“跨页面记住左侧栏内部滚动位置”这个能力，必须重新引入晚到的几何改写，那就先**放弃这个能力**。稳定性是更高阶要求。之后只有在能够做到“首屏前、非几何改写”的前提下，才考虑把它以更小的方式加回来。

**验收：**

- `theme/custom.js` 中不再存在运行时 sidebar projection 构造器
- `theme/index.hbs` 中不再存在内联 projection 启动逻辑
- 任意章节页在 enhancement JS 运行前就已经有正确的 sidebar 结构和 active state

---

### 阶段 3：恢复原生文档滚动

**目的：** 去掉第二类首屏不稳定来源：运行时 scroll-root 重映射。

**文件：**

- 修改：`theme/custom.js`
- 修改：`theme/custom.css`
- 修改：`scripts/test-site-render.sh`

**改动：**

1. 删除 `installInternalScrollerBridge()` 以及全部 `defineScrollBridgeProperty(...)` 覆盖
2. 停止覆盖：
   - `document.scrollingElement`
   - `window.pageYOffset`
   - `window.scrollY`
   - `document.documentElement.scrollTop`
   - `document.body.scrollTop`
   - `window.scrollTo`
   - `window.scrollBy`
3. 把 reader 的滚动行为切回 document scroll root
4. 审核所有当前耦合 `#mdbook-reader-scroll` 的逻辑，重点包括：
   - hash target 滚动
   - progress bar 更新
   - outline scroll spy
   - 所有读写 `scrollTop` 的代码
5. 如有必要，保留 `#mdbook-reader-scroll` 作为布局包装层，但它不能再承担语义上的 scroll root

**验收：**

- 页面使用浏览器原生滚动模型也能正常工作
- hash 跳转、进度条更新和 outline 状态在没有 scroll-root 覆盖的情况下仍然正确
- `theme/custom.js` 中不再含有 scroll bridge 属性覆盖

---

### 阶段 4：首屏相关 CSS 收口

**目的：** 防止结构修复后又被 CSS 重新带出启动位移。

**文件：**

- 修改：`theme/custom.css`
- 修改：`scripts/test-site-render.sh`

**改动：**

1. 删除或门控与 sidebar width / reader left offset 绑定的布局类 transition
2. 只保留用户交互触发的 motion，不保留首屏触发的 motion
3. 确保 reader grid、progress bar、toolbar 在加载时就能从静态 CSS 变量解出正确几何

**验收：**

- 从左侧导航加载章节时，不再出现任何启动阶段的可见布局 transition
- hover / focus 等真正由交互触发的动画仍然存在

---

## 验证计划

### 必跑命令

1. `npm run build:site`
2. `npm run test:site`
3. `sh scripts/test-preview-build.sh`

### 手工浏览器 QA

至少检查以下跳转：

1. `foreword.html -> chapter-01`
2. `chapter-01 -> chapter-02`
3. `chapter-04 -> chapter-05`
4. `general-conclusion -> glossary`

每次跳转都确认：

1. 没有可见的 rail 或整页闪动
2. 首屏即有正确 active row
3. 没有延迟发生的 left-offset 校正
4. progress bar 和 sticky header 仍然正常
5. 章节内 hash 链接仍然能正确定位

### 建议补充的回归断言

扩展 `scripts/test-site-render.sh`，锁定：

1. 生成页中仍然存在 `.reader-sidebar-projection`
2. `theme/index.hbs` 不再包含 inline projection bootstrap
3. `theme/custom.js` 不再包含：
   - `installSidebarProjection`
   - `defineScrollBridgeProperty`
   - `document.scrollingElement` 覆盖逻辑
4. `package.json` 与 `scripts/preview.sh` 都调用了新的静态侧栏构建步骤
5. CSS 在 booting 状态下不对布局执行 transition

---

## 上线策略

### 推荐提交顺序

1. `fix: gate reader layout transitions during boot`
2. `build: inject static reader sidebar from mdbook toc`
3. `refactor: remove runtime sidebar reprojection`
4. `refactor: restore native document scroll model`
5. `test: lock static sidebar boot contract`

### 为什么要拆成多次提交

这次变更同时触及运行时行为和构建管线。拆小提交可以让你更容易定位下列回归：

- 构建产物注入问题
- 导航 active-state 逻辑问题
- 滚动行为问题
- 视觉 motion 契约问题

---

## 风险与缓解

### 风险 1：mdBook TOC 生成格式漂移

**缓解：** 把解析器严格收敛到本仓库当前使用的 `toc.html` 生成契约上，并用渲染断言锁住。

### 风险 2：丢失侧栏滚动位置记忆

**缓解：** 第一版接受这个取舍。之后如果要恢复，也只能以“首屏前、非重投影”的方式最小化加入。

### 风险 3：移除内部 scroller 后把 outline / progress 搞坏

**缓解：** 把 scroll-bridge 移除单独作为一个阶段，并给它配明确的浏览器 QA 和 grep 断言。

### 风险 4：`build:site` 与 preview 管线分叉

**缓解：** 新的侧栏注入脚本同时接入 `package.json` 与 `scripts/preview.sh`，并持续保持 `scripts/test-preview-build.sh` 通过。

---

## 建议执行方式

这件事建议按 **两次交付** 做，而不是一次性全改完：

1. **先止血**：启动态 transition 门控 + 移除重复 sidebar 启动路径
2. **再做结构修复**：静态侧栏注入 + 删除运行时重投影 + 恢复原生滚动

这样既能快速改善用户可感知的问题，也不会破坏第一性原理下的架构收敛。
