# Book Reader Design Tokens

## 结论

已基于当前确认版的图一（宽屏）与图二（窄屏）整理出一套可实施引用的 design tokens，机器可读文件见：

- [book-reader-design-tokens.json](/Users/edison/workspace/peakwalk/scm/gitlab/africa-book/docs/design-baselines/2026-06-09-reader/book-reader-design-tokens.json)

这套 tokens 的目标不是复刻一份“营销站 token”，而是把 landing page 的品牌体系约束，转译成“偏学术专著阅读器”的实现参数。

## 适用范围

这套 tokens 只服务于当前这组参考稿：

- 宽屏参考：[wide-reference.png](/Users/edison/workspace/peakwalk/scm/gitlab/africa-book/docs/design-baselines/2026-06-08-reader/wide-reference.png)
- 窄屏参考：[narrow-reference.png](/Users/edison/workspace/peakwalk/scm/gitlab/africa-book/docs/design-baselines/2026-06-08-reader/narrow-reference.png)

## 设计边界

### 1. 品牌一致性

- 必须沿用 landing page 的 logo 体系、蓝金橙主色关系、以及整体的“专业能源研究”气质。
- 当前批准版窄屏稿也使用横向完整 logo lockup，不使用紧凑 icon 作为默认稿。
- `compact logo` 只作为降级或极端窄宽度 fallback 预留，不属于当前批准稿。

### 2. 学术阅读优先

- 正文、章节层级、图、表、公式，优先服从学术阅读节奏。
- 视觉重点应从“品牌展示”切换为“信息组织、检索、定位、对照阅读”。
- 因此，品牌色更多承担“索引、强调、状态”作用，而不是大面积装饰。

### 3. 宽窄屏同体系

- 宽屏和窄屏必须共享同一套 figure / table / formula 语言。
- 差异只能来自布局折叠与密度变化，不能变成两套视觉系统。

## Token 结构

JSON 文件按 MECE 拆成这些层：

- `meta`：版本与来源说明。
- `references`：对应的批准稿图片路径。
- `primitives`：基础色、字号、字重、间距、圆角、阴影、断点。
- `semantic`：语义层，如文字、边框、状态。
- `layout`：站点级布局参数，如 header 高度、logo 宽度、sidebar 宽度。
- `components`：阅读器关键组件参数。
- `implementationHints`：实施时必须遵守的约束。
- `cssCustomProperties`：建议映射出的 CSS 变量。

## 实施时优先引用的组件 token

### Header

- 宽屏 logo 宽度：`138px`
- 窄屏 logo 宽度：`216px`
- header 高度：`56px`
- 桌面搜索框宽度：`420px`

这里的重点是：窄屏不是缩成图标，而是保留完整横向 logo，只压缩周边控件密度。

### Shell

- 基础左栏宽度：`256px`
- 宽屏左栏宽度：`320px`
- 右侧小节导航宽度：`256px`
- 正文最大宽度：`896px`

这保证宽屏维持“左章导航 / 中正文 / 右页内导航”的学术阅读三栏骨架。

### Figure

- figure card 圆角：`20px`
- media 区圆角：`16px`
- image 圆角：`6px`
- card padding：`14px`

图件必须像“学术插图卡片”，而不是普通内容图。窄屏也要沿用这一套，只改变堆叠方式。

### Table

- table shell 圆角：`16px`
- 表头底色：`brandBlueDeep`
- 表头文字：白色
- 外层仍保留轻壳体、边框、阴影

也就是说，窄屏表格不能退化成完全不同的移动端卡片风格；应优先保持与宽屏一致的表格壳体语言。

### Formula

- 公式盒保留浅边框、左侧品牌强调线、轻阴影
- label tracking：`0.16em`
- expression size：`clamp(14.4px, 1vw, 16.8px)`

这对应你此前强调的“视觉演示稿中必须包含公式设计”。

## 实施建议

### 1. 先映射，不要直接散写值

建议先把 `cssCustomProperties` 映射到 `:root` 或 reader scope，再让具体组件消费这些变量。这样后面如果还要继续压 header、目录抽屉或表格密度，不需要反复手改散值。

### 2. 先保三类关键一致性

先确保三件事完全一致：

- logo 体系一致
- figure / table / formula 体系一致
- 宽窄屏信息层级一致

如果这三件事先做稳，之后再调 padding、字号、断点，成本会低很多。

### 3. 窄屏只做“折叠”，不做“换皮”

窄屏实现时应理解为：

- 章节导航从侧栏折叠为 chapter bar / drawer
- 页内导航从右栏折叠为 inline card
- 图表公式从横向排布转为纵向堆叠

但视觉语言本身不换。

## 后续可直接引用的文件

- 中文说明：[book-reader-design-tokens.zh_CN.md](/Users/edison/workspace/peakwalk/scm/gitlab/africa-book/docs/design-baselines/2026-06-09-reader/book-reader-design-tokens.zh_CN.md)
- 机器可读 token：[book-reader-design-tokens.json](/Users/edison/workspace/peakwalk/scm/gitlab/africa-book/docs/design-baselines/2026-06-09-reader/book-reader-design-tokens.json)

## 可选下一步

如果你下一步要进入真实实施，我建议新 thread 直接要求两件事：

1. 先把这份 JSON tokens 映射到 `theme/custom.css` 的 reader 变量层。
2. 再分别按宽屏与窄屏，把 header、sidebar、outline、figure、table、formula 五组组件逐项对齐参考稿。
