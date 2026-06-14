## Why

当前 `/book/` reader 仍然会在浏览器首屏绘制之后重建左侧边栏，同时还会在启动阶段对影响布局几何的属性执行动画。这两件事叠加起来，会让读者在通过左侧导航切换章节时看到明显的闪动，使整本书的阅读体验显得不稳定、不精致。

## What Changes

- 把最终 `.reader-sidebar-projection` 标记从运行时 JavaScript 构建迁移到仓库自有的 post-build 注入步骤，由该步骤读取 `public/book/toc.html`。
- 在静态侧栏注入生效后，删除模板内联和 `theme/custom.js` 中的 runtime sidebar reprojection 路径。
- 增加一个启动期布局契约，在 reader shell ready 之前禁用首屏几何 transition。
- 本次发布保留当前 `#mdbook-reader-scroll` 模型；暂不移除 internal scroll bridge。
- 更新渲染断言，锁定新的静态侧栏和启动稳定性契约，覆盖源码与生成后的 `/public/book` 输出。

## Capabilities

### New Capabilities
- `book-reader-flash-stability`：`/book/` reader 在保持当前滚动模型不变的前提下，提供一个静态首屏侧栏契约，避免通过左侧导航切换页面时出现可见布局闪动。

### Modified Capabilities
- None.

## Impact

- 受影响源码：`theme/index.hbs`、`theme/custom.js`、`theme/custom.css`、`scripts/test-site-render.sh`、`scripts/preview.sh`、`package.json`
- 新的构建脚本：`scripts/build_static_reader_sidebar.mjs`
- 受构建影响的生成输出：`public/book/index.html`、`public/book/chapters/*.html`
- 不引入新的运行时依赖
- mdBook 仍然是导航真相来源，并继续负责生成 `toc.html`
