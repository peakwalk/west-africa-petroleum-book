## ADDED Requirements

### Requirement: Static sidebar projection before first paint
`/book/` reader MUST 在运行时 reader JavaScript 构建任何 sidebar row 之前，就从生成 HTML 中渲染出最终左侧导航 projection。生成后的书籍页面 MUST 包含 projected sidebar 标记以及当前页面对应的 active-row 状态。

#### Scenario: Chapter page ships with projected sidebar markup
- **WHEN** 打开一个生成后的 `/book/chapters/*.html` 页面
- **THEN** 页面在运行时 reader enhancement 代码执行前，就已经包含该页面对应 active row 的 `.reader-sidebar-projection` 标记

#### Scenario: Root index page ships with projected sidebar markup
- **WHEN** 打开生成后的 `/book/index.html` 页面
- **THEN** 页面已经包含 `.reader-sidebar-projection` 标记，而不是依赖运行时 projection 构建

### Requirement: No runtime sidebar reprojection after paint
`/book/` reader MUST NOT 在页面绘制后，通过 `theme/index.hbs` 的 inline 启动逻辑或 `theme/custom.js` 再次重建 sidebar projection 结构。Reader enhancement 代码 MAY 给 projected rows 绑定非结构性行为，但 MUST NOT 在运行时重建 sidebar section 和 row tree。

#### Scenario: Template does not bootstrap sidebar projection
- **WHEN** 检查书籍模板源码
- **THEN** 模板中不包含会重建 projected sidebar row 的 inline `bootstrapSidebarProjection()` 路径

#### Scenario: Reader enhancement script does not reproject the sidebar
- **WHEN** 检查 reader enhancement 源码
- **THEN** 源码中不包含会在页面加载后重建 sidebar projection 结构的运行时 `installSidebarProjection()` 路径

### Requirement: Boot-time geometry transitions are suppressed
`/book/` reader MUST 在启动阶段抑制影响布局几何的 transition，直到 reader shell ready。凡是与 sidebar width 或 reader left-offset 相关的几何属性，在初始加载期间 MUST NOT 执行动画。

#### Scenario: Boot state disables reader geometry motion
- **WHEN** 生成后的书籍页面处于 boot state
- **THEN** `padding-inline-start`、`width` 和 `margin-inline-start` 等 reader 几何 transition 会在 boot 完成前被禁用

#### Scenario: Stable first paint during left-rail navigation
- **WHEN** 读者通过左侧导航跳转到另一个章节
- **THEN** 新页面加载时不会因为延迟的 sidebar projection 或启动期布局动画而出现可见的整页闪动

### Requirement: Current scroll model remains unchanged in v1
`v1` 的 flash stabilization 变更 MUST 保留当前 `#mdbook-reader-scroll` 模型，并且 MUST NOT 在同一次发布里移除 internal scroll bridge。

#### Scenario: Scroll bridge remains present
- **WHEN** 在 `v1` 变更后检查 reader enhancement 源码
- **THEN** internal scroller bridge 仍然存在，并且该变更没有把页面迁回浏览器原生 document scrolling
