## Context

首页搜索区块由 `scripts/shared/homepage-content.mjs` 生成，并使用前面拆分出的 landing CSS。当前区块的搜索跳转目标其实已经正确，但它在两个明显点上与设计参考图不一致：标题重复显示，以及独立的提交按钮。

英文首页的 `Browse by Topic` 区块也来自同一个生成源文件，并且仍然沿用更早的信息架构草稿：一个很大的 narrative heading，加上 10 张 topic 卡片。批准的参考图则是一个紧凑的区块标题，加上 6 张带图标的卡片。

底部的 `summary-modules` 行也仍然停留在旧版布局：4 张等宽卡片、沿用全大写 kicker 风格、普通圆点列表，而且没有设计稿里可见的 CTA 链接。提供的参考图则使用了第二张更宽的卡片、Title Case 卡片标题、绿色勾选列表标记，以及 3 条底部动作链接。

这次改动刻意保持很小的范围。目标不是再次重做整页信息架构，而是把搜索标题/搜索框组合方式、英文首页 `Browse by Topic` 的区块结构，以及英文首页 `summary-modules` 的收尾卡片行一起对齐到参考图，同时保留现有本地化文案、跳转目标和查询参数行为。

## Goals / Non-Goals

**Goals:**
- 在现有 landing 体系内，尽可能贴近提供的参考图来对齐首页搜索标题和搜索框构图。
- 在现有 landing 体系内，尽可能贴近提供的参考图来对齐英文首页 `Browse by Topic` 的标题和 6 卡片布局。
- 在现有 landing 体系内，尽可能贴近提供的参考图来对齐英文首页 `summary-modules` 的卡片比例、标题样式、列表标记和 CTA。
- 保持现有 `search` 查询参数契约和书籍跳转目标不变。
- 保持 topic 卡片背后的章节跳转目标不变。
- 保持 summary 卡片 CTA 仍然落到现有的首页锚点或章节库路由。
- 保留本地化文案，以及搜索框下方的搜索范围 chips 链接。
- 让法文兼容首页继续保持当前的 topic fallback 布局。
- 把改动限制在首页源模板、区块级 CSS 和针对性验证里。
- 在平板和手机宽度下继续保持可用的响应式行为。

**Non-Goals:**
- 重做搜索框下方的 chips。
- 修改书籍阅读器内的实际搜索体验。
- 引入 JavaScript 自动补全或新的搜索后端。
- 把法文兼容首页的 topic 区块一并重做成英文设计稿。
- 为了支持 summary 卡片 CTA 而新建独立的 updates/roadmap 后端。
- 重绘与本区块无关的首页模块。

## Decisions

### Decision: 继续以首页生成器标记为单一事实来源
新的搜索区块结构会在 `scripts/shared/homepage-content.mjs` 中实现，并通过现有站点构建流程落到生成页面里。不会手改生成后的 `index.html` 变体。

Alternative considered:
- 直接修改生成后的首页文件。拒绝，因为它会和生成器脱节，并在下次构建时被覆盖。

### Decision: 用一体化搜索外壳替换独立提交按钮
表单会渲染成一个统一的圆角搜索外壳，内部包含前置提交控件/图标和搜索输入框。这样最接近参考图，同时仍保留点击或回车提交的原生表单行为。

Alternative considered:
- 保留当前右侧 CTA 按钮，只调整样式。拒绝，因为设计参考图本身就没有独立的搜索 CTA，整体布局仍会不对。

### Decision: 区块只显示一个可见标题，同时保留可访问标签
这个区块将不再把 eyebrow 作为可见文本输出，而是只保留居中的 `h2` 作为唯一可见标题。表单继续保留屏幕阅读器标签，避免可访问性依赖 placeholder。

Alternative considered:
- 同时保留 eyebrow 和标题，再收紧间距。拒绝，因为“重复标题”本身就是当前和设计稿不一致的原因之一。

### Decision: 样式改动限制在搜索区块和响应式覆盖层
布局、间距、图标对齐和胶囊输入框样式会通过 `assets/css/landing.discovery.css` 中的搜索区块选择器处理，只在平板/手机 CSS 里加最小补充规则。

Alternative considered:
- 全局修改共享 heading 或 button token。拒绝，因为会把回归风险扩散到本区块之外的首页模块。

### Decision: search-scope chip 使用区块本地的内联 SVG 图标集
`search-scope` 芯片会渲染自己的一组内联 SVG 图标，而不是混用现有 hero 图标和 homepage sprite 资源。现有资源的隐喻、描边风格和强调色不一致，即使只调 CSS，也仍然会和批准参考图里的蓝色单色图标有明显偏差。

Alternative considered:
- 直接复用现有 homepage sprite 和 hero SVG 资源。拒绝，因为它们带有混合的金色强调和不一致的图标语言，无法精确贴近设计稿。

### Decision: 用 6 张 reference 卡片替换英文首页的 topic editorial 布局
英文首页 topic 区块将不再渲染“大叙事标题 + 10 卡片”的旧结构，而是改成一个可见区块标题、6 张按设计稿顺序排列的卡片，以及更短、更适合紧凑卡片的描述文案。

Alternative considered:
- 保留 10 张卡片，只压缩间距。拒绝，因为设计稿变化的不只是密度，而是整个区块结构。

### Decision: 把 topic 卡片重绘限制在英文首页变体
新的 6 卡片布局只会用于英文首页生成逻辑。法文兼容首页会继续使用现有 compact fallback 卡片，直到后续拿到独立的法文参考图。

Alternative considered:
- 直接把新的英文 topic 卡片设计同时套用到两个语言版本。拒绝，因为法文兼容首页本来就是过渡结构，内容集和批准参考图也都不相同。

### Decision: 为 6 张 topic 卡片使用独立的内联 SVG 图标集
这组 topic 卡片会渲染自己的一套内联 SVG 图标，分别覆盖 value chain、fiscal regimes、national oil companies、upstream operations、governance 和 country analysis。这样可以在不依赖混杂旧 sprite 资源的情况下，更稳定地贴近设计稿里的蓝色描边图标语言。

Alternative considered:
- 复用现有 homepage sprite 和 chapter icon。拒绝，因为现有资源没有一组完整且风格统一的对应图标。

### Decision: 保留现有 summary 内容集，但把它重排成批准的 4 卡片构图
`summary-modules` 仍然保留当前英文首页的 4 组内容：latest updates、current edition、topics covered 和 future development。这次改动聚焦在结构和表现层，而不是做新的文案重写；同时为其中 3 张卡片补上设计稿里可见的 action links。

Alternative considered:
- 直接把 summary 文案完全改写成和设计稿逐字一致。拒绝，因为当前内容本身已经覆盖了设计稿表达的意图，用户请求的重点是视觉对齐而不是大范围内容重写。

### Decision: summary 卡片的新 CTA 复用现有内部路由
新的 summary CTA 不会发明新页面。`View all updates` 和 `Learn more` 会指向现有章节库，`View all topics` 会跳回首页 topics 区块。

Alternative considered:
- 先放占位或空链接，等以后有 updates 页面再接上。拒绝，因为既然把 CTA 做成可见元素，就应保持可点击且有意义。

### Decision: 把 summary 标题样式从 topic kicker 样式中拆出来
`summary-card-eyebrow` 将不再与 topic kicker 共享同一套全大写强调样式。summary 卡片标题需要独立的深色、Title Case 排版，才能贴近提供的参考图。

Alternative considered:
- 保留统一的 kicker 样式，只调整卡片间距。拒绝，因为这个全大写、强调色的标题风格本身就是和设计稿差异最大的点之一。

## Risks / Trade-offs

- [不同语言的 placeholder 长度不同] -> 保持输入框弹性，不在框内塞一个固定宽度按钮，避免法语文本挤压。
- [移除独立 CTA 后，明显点击目标会变化] -> 让前置图标/按钮可聚焦，并保留标准的回车提交行为。
- [区块级 CSS 在小屏下可能漂移] -> 添加明确的窄屏覆盖规则，并验证重建后的英文/法文首页输出。
- [桌面端改成 6 卡片后，每张卡片的可用宽度会比原来的 5 列更窄] -> 缩短文案、压紧排版，并让平板/手机继续通过现有响应式规则回落到更少列数。
- [新增英文 topic 版式可能误伤法文兼容卡片] -> 把新样式挂到 topic-reference modifier class 上，并补一条法文首页“不应出现 reference-grid class”的断言。
- [新增 CTA 可能暗示还不存在的独立页面] -> 复用当前已有的章节库和首页锚点路由，保证 CTA 全部可用。
- [summary 的桌面布局现在依赖不对称列宽] -> 平板和手机继续沿用现有两列/一列回退，不把这种不对称比例强行带到小屏。

## Migration Plan

1. 补齐这次搜索区块对齐改动的 OpenSpec proposal、design、spec 及双语配套文件。
2. 更新首页生成器标记、区块级 CSS、英文 topic 卡片的数据/图标辅助文件，以及 summary 卡片 CTA 标记。
3. 通过正常的站点构建流程刷新生成后的首页输出。
4. 运行针对首页标记和 CSS 预期的站点验证。
5. 如果效果不可接受，直接回滚首页 search/topic/summary 标记、辅助数据和区块级 CSS；这次不涉及任何数据迁移。

## Open Questions

- None for this change. 提供的参考图已经足够明确，可以让实现保持范围可控且结果确定。
