## Why

当前 book 页搜索仍由 mdBook 默认的 `searcher.js` 驱动，它输出的是通用覆盖层，并把搜索行为、键盘处理和 URL 管理耦合在一起，和这次确认的 `SearchBox` 交互模型不一致。我们需要保留本地 mdBook 搜索索引，但在源码层重写交互体验，补齐聚焦过滤、显式关闭、高亮结果和清空输入等行为。

## What Changes

- 在书籍模板中移除默认 mdBook `searcher.js` 的交互接管，改由 `theme/custom.js` 实现自定义 `SearchBox`。
- 保留 `searchindex.js` 作为本地数据源，但在前端实时按 `title`、`body` 和 `breadcrumbs` 过滤。
- 为书籍工具栏搜索补充显式 `focused` 状态、清空按钮、外部点击关闭、结果计数、空态和结果高亮行为。
- 将结果面板改为定位在输入框下方的绝对定位下拉层，而不是当前固定定位的 overlay root。
- 更新站点渲染断言，确保主题源码和生成后的 `/public/book` 输出都符合新的搜索契约。

## Capabilities

### New Capabilities
- `book-searchbox`：用于 `/book/` 页面的自定义工具栏搜索框，基于本地 mdBook 索引数据提供聚焦式下拉搜索和高亮结果。

### Modified Capabilities
- None.

## Impact

- 受影响源码：`theme/index.hbs`、`theme/custom.js`、`theme/custom.css`、`scripts/test-site-render.sh`
- 通过构建影响的生成产物：`public/book/*`
- 不引入新的运行时依赖
- mdBook 仍然负责内容与索引生成
