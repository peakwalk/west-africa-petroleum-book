# Book SearchBox Design

**Date:** 2026-06-14

**Goal**

将当前由 mdBook 控制的书籍搜索行为替换为主题层自有的 `SearchBox`，保留本地搜索索引，但按已确认 prompt 实现状态管理、过滤、清空、外部点击关闭、下拉渲染和结果高亮。

## Context

当前 `/book/` 工具栏搜索只做了一半定制：`theme/custom.js` 负责把搜索输入框搬进工具栏槽位，但真正的搜索行为和结果面板仍由 mdBook 生成的 `searcher.js` 控制。这种拆分导致 UX 很难稳定接管，也不符合本次确认的交互契约。

仓库已经通过 `searchindex.js` 提供了本地搜索所需的全部数据，其中的 document store 暴露了 `title`、`body` 和 `breadcrumbs`。因此可以继续让 mdBook 负责索引，只重写工具栏搜索交互层。

## Scope

In scope:

- `theme/index.hbs` 中的书籍工具栏搜索标记
- `theme/custom.js` 中的书籍工具栏搜索行为
- `theme/custom.css` 中支持搜索下拉层的样式
- `scripts/test-site-render.sh` 中的渲染断言

Out of scope:

- mdBook 索引生成
- 首页搜索
- 除确定性本地过滤之外的搜索排序策略
- 与搜索无关的更大范围阅读器外壳改造

## Design Decisions

### 1. 由主题层拥有搜索控制器

我们会在模板中停止加载 mdBook `searcher.js`，并在 `theme/custom.js` 内实现 `SearchBox` 控制器。这样可以避免事件控制权冲突，并让搜索实现和书籍外壳其他行为处于同一源码层。

### 2. 基于序列化文档做纯本地过滤

我们会懒加载 `searchindex.js`，把 `window.search.index.documentStore.docs` 转成普通记录，然后在 `title`、`body` 和 `breadcrumbs` 上做不区分大小写的过滤。`breadcrumbs` 同时作为结果中的 section/category 标签显示。

### 3. 对齐 prompt 的下拉行为

搜索外壳将显式维护 `query`、`focused`、`results` 和 `activeIndex` 状态。结果下拉层只在聚焦且查询非空时渲染，通过文档级 `mousedown` 外部点击检查关闭，并提供不会导致失焦的清空按钮。

### 4. 保留目标页高亮

结果链接会附带 `highlight` 查询参数，`theme/custom.js` 会使用 `Mark` 在目标页高亮选中的关键词。这保留了当前阅读器里有价值的一部分行为，同时不会把 mdBook 旧的整套搜索 URL 流程带回来。

## Verification

- `npm run test:site`

## Risks

- 如果键盘快捷键没有被完整重做，移除 `searcher.js` 可能带来回归。
- 自定义下拉层选择器必须和现有工具栏样式稳定共存。
