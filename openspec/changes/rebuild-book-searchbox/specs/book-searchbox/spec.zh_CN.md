## ADDED Requirements

### Requirement: Query-driven local filtering
书籍搜索框 MUST 在查询变化时实时过滤本地 mdBook 索引记录。匹配 MUST 不区分大小写，并同时检查已索引的 `title`、`body` 和 `breadcrumbs` 字段。当去除首尾空白后的查询为空时，结果集 MUST 为空，而不是展示全部索引项。

#### Scenario: Query matches across indexed fields
- **WHEN** 读者输入一个非空查询，并且该查询出现在结果标题、正文摘录或 breadcrumbs 标签中
- **THEN** 搜索框只返回索引文本中包含该查询的记录，且不区分大小写

#### Scenario: Empty query clears results
- **WHEN** 读者删除搜索输入中的全部文本
- **THEN** 搜索框保存空结果集，并且不展示全部索引项

### Requirement: Focused dropdown visibility and dismissal
书籍搜索框 MUST 只在输入框聚焦且去除首尾空白后的查询非空时显示结果面板。用户按下 `Escape` 或点击搜索输入外壳和结果面板之外的区域时，面板 MUST 关闭。关闭行为 MUST 通过 `mousedown` 监听实现，而不是依赖输入框 `blur`。

#### Scenario: Focus plus query opens the panel
- **WHEN** 搜索输入已聚焦且去除首尾空白后的查询至少包含一个字符
- **THEN** 结果面板以下拉形式直接显示在输入框下方

#### Scenario: Outside click closes the panel
- **WHEN** 用户在搜索输入外壳和结果面板之外的目标上按下鼠标
- **THEN** 搜索框将输入状态标记为未聚焦并关闭下拉层，而不是等待 `onBlur` 回调

### Requirement: Clear action and focus-preserving input state
书籍搜索框 MUST 在查询非空时在输入框内部渲染清空控件。激活清空控件时 MUST 清空查询，并把焦点返回给搜索输入。搜索 UI MUST 通过 JavaScript 控制的状态类在聚焦时略微变宽，而不是单纯依赖 CSS `:focus`。

#### Scenario: Clear control resets the query without blur
- **WHEN** 查询非空且用户激活清空控件
- **THEN** 该控件阻止 `mousedown` 导致的失焦，清空查询值，并重新聚焦输入框

#### Scenario: Focus state changes input width
- **WHEN** 搜索输入进入或离开聚焦状态
- **THEN** 搜索外壳切换一个带状态语义的类来控制扩展后的输入宽度

### Requirement: Result rendering and highlighting
书籍搜索框 MUST 为每个结果渲染类型图标、高亮标题文本、可见 breadcrumbs 标签和高亮摘录。高亮逻辑 MUST 使用不区分大小写的查询正则拆分文本，并用 `<mark>` 元素包裹每个命中。结果面板 MUST 同时渲染结果计数头部；当没有命中结果时，MUST 渲染带图标和消息的空态。

#### Scenario: Matching results show highlighted fields
- **WHEN** 查询匹配到一个或多个索引记录
- **THEN** 每个渲染结果都包含类型标记、带 `<mark>` 的标题、breadcrumbs 标签以及带 `<mark>` 的摘录

#### Scenario: No matches show an empty state
- **WHEN** 查询非空且没有任何索引记录匹配
- **THEN** 下拉层保持打开，并渲染结果计数头部以及带图标和说明文字的空态行

### Requirement: Keyboard navigation of visible results
书籍搜索框 MUST 在下拉层可见时支持键盘导航。`ArrowDown` 和 `ArrowUp` MUST 移动当前激活结果索引，`Enter` MUST 打开当前激活结果，`Escape` MUST 关闭面板并让输入框失焦。

#### Scenario: Arrow keys move the active result
- **WHEN** 下拉层可见且用户按下 `ArrowDown` 或 `ArrowUp`
- **THEN** 搜索框更新当前激活结果，而不会提交表单

#### Scenario: Enter opens the active result
- **WHEN** 下拉层可见、已有激活结果，且用户按下 `Enter`
- **THEN** 读者跳转到该结果目标
