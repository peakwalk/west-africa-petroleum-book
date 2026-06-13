## 1. 搜索模板与验证更新

- [x] 1.1 更新 `theme/index.hbs`，加入 clear 按钮，保留现有书籍搜索 id，并停止加载 `searcher.js`
- [x] 1.2 更新 `scripts/test-site-render.sh`，断言新的搜索标记、CSS 钩子、JS 钩子，以及 `searcher.js` 不再被引入

## 2. 自定义 SearchBox 实现

- [x] 2.1 用主题层自有状态控制器替换 `theme/custom.js` 中当前的工具栏搜索胶水逻辑，懒加载 `searchindex.js`，并按 `title`、`body` 和 `breadcrumbs` 过滤
- [x] 2.2 在 `theme/custom.js` 中渲染高亮结果行、结果计数、空态、clear 按钮行为、外部点击关闭和键盘导航
- [x] 2.3 通过给结果链接附加 `highlight` 查询参数并在目标页加载时应用 `Mark`，保留跳转后的高亮行为

## 3. 样式与验证

- [x] 3.1 更新 `theme/custom.css`，让搜索槽位通过 JS 控制的聚焦状态扩展宽度，并把结果面板做成输入框下方的绝对定位下拉层
- [x] 3.2 为结果行、激活状态、图标标签、摘录文本和空态补充最小 CSS 支撑
- [x] 3.3 运行 `npm run test:site`，修复所有回归直到构建和渲染断言通过
