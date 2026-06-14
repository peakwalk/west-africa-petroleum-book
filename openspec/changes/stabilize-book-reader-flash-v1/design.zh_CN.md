## Context

当前左侧导航使用了两条独立的 runtime projection 路径：

- `theme/index.hbs` 里的内联 `bootstrapSidebarProjection()`
- `theme/custom.js` 里的第二条 `installSidebarProjection()` 路径

这两条路径都会在页面解析后重建 `.reader-sidebar-projection`，并依赖运行时几何计算来对齐侧栏滚动位置。同时，`.reader-main` 和 `.book-progress` 上影响布局几何的 transition 在启动阶段就已经启用，所以任何晚到的 left-offset 或 projection 校正都会被读者看见。

仓库里已经有一个稳定的生成导航源：`public/book/toc.html`。因此这里非常适合改成构建期 projection，而不是客户端重建。

## Goals / Non-Goals

**Goals:**
- 确保生成后的书籍页面在客户端 JavaScript 运行前就已经包含最终侧栏 projection 标记。
- 从模板和 `theme/custom.js` 中删除 runtime sidebar reprojection。
- 防止首屏几何 transition 在启动阶段把 reader 布局动画化。
- 在 `v1` 中保留当前 `#mdbook-reader-scroll` 模型以及现有 outline / progress 逻辑。

**Non-Goals:**
- 在这次变更里把 reader 恢复为浏览器原生 document scrolling。
- 围绕新的 scroll root 重写 hash 导航、进度条或 outline scroll-spy。
- 做超出稳定首屏所需范围之外的 sidebar 视觉重设计。
- 替换 mdBook 作为导航真相来源。

## Decisions

### 1. 使用仓库自有的 post-build 注入器，而不是修改 mdBook 内部

仓库已经通过 `strip_mdbook_onunload.mjs`、`build_reader_page_meta.mjs` 等脚本做 post-build 处理。新增 `scripts/build_static_reader_sidebar.mjs` 延续了这一模式，也把变更范围控制在仓库自有的构建工具层。

备选方案：
- 直接修改 mdBook 输出生成逻辑。拒绝原因是这会把变更扩大到仓库外部，也会让导航契约更难在本地快速迭代。

### 2. 在 `v1` 中保留当前滚动模型

当前最大回归面来自 internal scroller bridge。它与 hash 滚动、进度条计算和依赖滚动状态的 UI 逻辑纠缠较深。因此 `v1` 的目标是在不碰 `installInternalScrollerBridge()` 的前提下稳定首屏。

备选方案：
- 在同一次修复里顺手移除 scroll bridge。拒绝原因是那样会把两个高风险改动绑在一起，回归很难隔离。

### 3. 用更简单的契约保留侧栏视口位置

旧的 projection 逻辑会保存“行相对偏移”，然后在 reprojection 之后再去改 visible rail。`v1` 中 reader 应改为保存更简单的 `reader-sidebar-scroll-top`，并在不重建侧栏的情况下恢复它。这样既能让当前阅读区域保持可见，又不会重新引入 projection 时几何计算。

备选方案：
- 完全放弃侧栏位置持久化。拒绝原因是这会在较低章节和 back matter 页面上引入新的可见回退。

### 4. 通过模板自有的状态类在启动阶段禁用布局 transition

当前 `padding-inline-start`、`width` 和 `margin-inline-start` 上的 motion 在 reader 可交互后仍有价值，但在首屏阶段不应生效。一个只用于启动期的 body class 可以以最小、可回退的方式，在初始化完成前屏蔽这些 transition。

备选方案：
- 彻底删除这些 transition。拒绝原因是页面稳定后，它们对用户触发的 sidebar 状态变化仍然有价值。

## Risks / Trade-offs

- [静态注入可能与 mdBook TOC 输出漂移] -> 让注入器解析逻辑严格收敛到当前生成的 `toc.html` 结构上，并用渲染断言锁住。
- [如果侧栏滚动恢复执行得太晚，仍可能带来可见移动] -> 通过模板内的小脚本，在已渲染好的 projected markup 上尽早恢复，而不是等到 `DOMContentLoaded`。
- [保留 internal scroller 会暂时留下技术债] -> 在 `v1` 中接受这个取舍，因为当前最紧急的目标是消除可见闪动；滚动模型清理作为后续 change 处理。
- [生成页会因为重复内联侧栏 HTML 而变大] -> 接受这个取舍，因为本仓库章节数量不大，而首屏稳定性的收益更高。
