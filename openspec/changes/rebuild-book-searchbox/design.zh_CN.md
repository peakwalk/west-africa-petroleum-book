## Context

`/book/` 阅读器已经通过 `theme/custom.js` 把 mdBook 的搜索框挪进了头部槽位，但真正的搜索和结果渲染仍由生成的 `searcher.js` 控制。现在的拆分方式让搜索体验很难被主题层稳定接管，因为自定义主题在搬运 DOM，而生成脚本仍假设自己拥有焦点、结果层位置和键盘行为的控制权。

这次确认的交互模型比 mdBook 默认实现更窄、更确定：

- 结果基于本地数据实时过滤
- 只有输入框聚焦且查询非空时才展示面板
- 清空查询时不能让输入框失焦
- 外部点击必须关闭面板，且不能依赖 `blur`
- 下拉层必须直接渲染在输入框下方，而不是分离的固定 overlay

现有 mdBook 索引已经包含需要的字段：`title`、`body` 和 `breadcrumbs`。在这个仓库里，`breadcrumbs` 就是 prompt 中 section/category 的最自然映射，因此没有必要修改索引生成过程。

## Goals / Non-Goals

**Goals:**
- 保留 mdBook 生成的 `searchindex.js` 作为搜索数据源。
- 用主题层自定义 `SearchBox` 替换 mdBook `searcher.js` 行为。
- 对齐已确认 prompt 中的状态、过滤、关闭、清空、高亮和可选键盘交互。
- 将实现范围收敛在主题源码和渲染断言。

**Non-Goals:**
- 不把搜索重做成服务端或复杂模糊检索。
- 不修改 mdBook 的索引生成流水线。
- 不顺带重设计搜索框之外的阅读器工具栏或章节布局。
- 不为搜索单独引入 React 一类框架运行时。

## Decisions

### 1. 从主题中移除 `searcher.js`，改在 `theme/custom.js` 中实现

`searcher.js` 同时控制 DOM、焦点、键盘、URL 状态和结果标记。如果只在它外面补丁，会形成两个控制器争抢同一组节点。更稳的方式是在 `theme/index.hbs` 中停止加载 `searcher.js`，并在 `theme/custom.js` 中直接实现需要的 `SearchBox` 逻辑，因为阅读器外壳的其他行为本来就已经放在这里。

备选方案：
- 保留 `searcher.js`，再叠加一层事件监听。否决，因为它会继续保留和新需求不兼容的 `keyup`、`keydown` 与结果 overlay 假设，焦点和选择行为很容易打架。

### 2. 把 `searchindex.js` 文档数据当作纯本地记录使用

满足这个 prompt 并不需要 Elasticlunr 的排序搜索 API。生成出来的 `window.search.index.documentStore.docs` 已经直接暴露了 `title`、`body` 和 `breadcrumbs`，而这个仓库的索引总量也只有大约一百条。新的搜索框会懒加载 `searchindex.js`，把这些文档转换为本地记录，并做不区分大小写的本地过滤。

备选方案：
- 复用序列化索引里的 Elasticlunr 排序。否决，因为 prompt 要的是可控、确定的过滤行为，而不是复杂相关性排序；纯过滤也更容易调试和维护。

### 3. 使用 `breadcrumbs` 作为 section/category 标签

Prompt 要求能匹配 section/category 字段，并在结果项里展示 section label。本仓库 mdBook 索引里现成保存了层级信息，比如 `Chapter 1 ... » 1.1.3- Main challenges`。新的结果渲染器会把 `breadcrumbs` 同时作为可搜索字段和可见 section label。

备选方案：
- 生成新的专用 category 字段。否决，因为这会把变更范围扩展到 mdBook 索引层，但对这次交付的 UX 收益不够大。

### 4. 继续通过 `mark.min.js` 保留目标页高亮

虽然 prompt 没要求 URL 驱动的搜索状态，但在跳转后的目标页高亮所选查询词仍然是当前行为里有价值的一部分。结果链接会附带 `?highlight=<query>`，`theme/custom.js` 会在页面加载时读取该参数并对正文应用 `Mark`。

备选方案：
- 完全移除目标页高亮。否决，因为仓库已经在发版中携带 `mark.min.js`，保留页内强调的成本很低。

## Risks / Trade-offs

- [本地子串过滤比排序搜索更简单] -> 接受这个取舍，因为索引体量小，而且 prompt 明确优先交互逻辑而不是高级相关性排序。
- [搜索索引脚本较大] -> 只在第一次使用搜索时懒加载 `searchindex.js`，并缓存解析后的记录。
- [移除 `searcher.js` 可能回归已有键盘快捷键] -> 在自定义控制器中重做 `/`、`s`、`Escape`、方向键和 `Enter` 行为，并用源码断言覆盖这些关键点。
- [搜索样式已经有仓库自己的覆盖] -> 选择继续围绕现有 `toolbar-search-slot` 结构做改动，而不是发明一套全新的外壳。

## Migration Plan

1. 更新 `theme/index.hbs` 中的搜索标记，加入 clear 按钮，并停止加载 `searcher.js`。
2. 用 `theme/custom.js` 中的主题级 `SearchBox` 控制器替换当前搜索槽位逻辑，负责加载本地文档、过滤、渲染、关闭和高亮。
3. 更新 `theme/custom.css`，让输入框根据状态变宽，并将结果面板做成输入框下方的绝对定位下拉层。
4. 更新 `scripts/test-site-render.sh`，断言新的源码标记和生成输出。
5. 运行 `npm run test:site` 重建站点并验证新的搜索行为契约。

## Open Questions

- None. 当前唯一的歧义是 section/category 字段映射，这次实现已决定直接使用 `breadcrumbs`。
