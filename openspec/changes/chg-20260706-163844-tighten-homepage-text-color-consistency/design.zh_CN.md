## Context

当前 landing 样式已经在 `assets/css/landing.base.css` 里定义了一部分首页配色，包括 `--homepage-heading-text`、`--homepage-primary-text`、`--brand-blue` 和 `--brand-blue-deep`。但白底首页模块仍然额外混用了很多写死颜色，例如 `#17346f`、`#244da3`、`#2f56a4`、`#2f67f6`、`#4a5d78`、`#61708a` 和 `#7287b3`，而这些值承担的视觉角色其实非常接近。

这种漂移现在最明显地出现在 header navigation、stakeholder strip、country cards、search chips、topic cards 和收尾的 summary row 之间。批准过的首页信息架构和区块构成并不需要再次重做；真正的缺口是说明性文案看起来经常和交互文字一样强调，而不同交互元素之间也缺少一条清晰统一的 link color 基线。

对批准设计稿做第二轮截图对比后，还暴露出一个更窄的问题：第一轮清理把一部分承载内容的短副信息和空状态文案压得过于接近 metadata 角色，而共享 CTA 和 chip-like controls 虽然更一致了，却也稍微安静过头。所以下一轮需要在保持一致性的同时，避免白底区块看起来比参考稿更轻、更稀。

第三轮截图对比把剩余偏差进一步收窄了：现在整页层级已经大体正确，但 country grid、topic cards 和收尾 summary row 相比批准参考稿仍略轻、略松。所以下一轮不需要再重开整页层级，而是只对这三组卡片做最后一档密度收尾。

用户现在还额外提供了一组明确的 hero-stat 图标素材 `design_replicated_icons_v10`。这个需求不再是层级微调，而是对六个 hero metric 图标做直接资源对齐，因此应复用现有 hero 图标挂载点完成替换，而不是重写 hero metric 的结构。

用户现在还提供了一组 `topic-card` 图标素材 `oil_icons_v8_thicker_third_icon`。这组素材的评审说明明确指出，本轮只进一步加粗了第 3 个 `National Oil Companies` 图标，其余 5 个图标保持 v7 不变。因此首页 topic icons 应继续直接消费这组 SVG 资产，而不是继续手写一版内联 path，或依赖页面端去缩放大尺寸 PNG。

## Goals / Non-Goals

**Goals:**
- 为首页白底区块定义一套一致的文本层级：标题、强调/实体文字、辅助正文、元信息和交互文字。
- 用更少的共享颜色角色或 token，替代各模块各自写死的近似蓝色。
- 恢复说明性文案与可点击文字之间更清晰的区分，覆盖 cards、strips、search chips 和 section-level CTA。
- 把改动控制在足够窄的范围内，确保现有布局、间距、字号、跳转目标和本地化文案保持不变。

**Non-Goals:**
- 不重做首页布局、区块顺序或卡片构成。
- 不调整 hero 图片、footer 结构、图标系统或内容策略。
- 不为整本书 reader 引入一套新的全局品牌色盘。
- 不修改首页搜索或导航相关的文案、目的地或任何后端行为。

## Decisions

### Decision: 为首页显式补齐 body、metadata 和 link text 角色
首页现在已经有 heading 和 emphasis 两档蓝色，但缺少对 body copy、metadata 和 interactive text 的显式共享角色。本次会在 `landing.base.css` 里补齐这些角色，让其他首页样式不再通过分散的一次性 hex 值去表达它们。

备选方案：
- 只复用现有的 `--homepage-primary-text`、`--brand-blue` 和 `--text-muted`。拒绝原因是这样仍然无法清楚界定 metadata 和 supporting body copy，而这正是当前漂移的来源。

### Decision: 强调蓝保留给实体标签和少量需要强调的标题，不再默认覆盖大部分说明性文案
白底卡片和白底区块里的说明性文字会回到更平静的 body/meta 色，而不是继续大量停留在 `--homepage-primary-text` 上。更强的首页蓝色只保留给标题、实体名和确实需要强调的标签。

备选方案：
- 维持当前大部分说明性文案都在中蓝色家族里，只统一链接颜色。拒绝原因是问题不只是 link 不统一，而是太多非交互文案看起来也像被强调。

### Decision: section links、card links 和 search chips 统一一条交互文字基线
白底区块里的交互文字默认会使用一条共享 link role，再配一条更深的 hover role，而不是由每个模块单独发明一组相邻蓝色。这样 section CTA、country links、topic links、summary links 和 search chips 才会被识别成同一套交互语言。

备选方案：
- 保留各模块独立的 CTA / link 蓝色，让模块更“有个性”。拒绝原因是用户这次反馈的核心就是感知上的不一致，而这些差异本身并没有传递真正有意义的产品层级。

### Decision: metadata 只保留给真正安静的辅助信息，不再覆盖承载内容的短副信息
日期、placeholder 和 helper label 可以继续使用更弱的 metadata 角色。相对地，country 缩写、无烃产出提示之类虽然短，但它们本身仍然属于内容，因此应留在 supporting body 角色里，避免卡片相比批准参考图显得发灰、发空。

备选方案：
- 为了最大化层级分离，把所有次级单行文字都压到 metadata。拒绝原因是截图对比已经证明，这会让 country grid 和 summary row 更像“缺墨”，而不是更清晰。

### Decision: 先用字重、字号和边框对比恢复 CTA/控件的可点击感，而不是继续加新颜色
下一轮会通过 font weight、局部字号调整，以及稍微更明确的 border/shadow 处理来强化共享 CTA 和 chip-like controls。这样既能保住交互家族的一致性，也能把设计稿里那种更利落的可点击感补回来。

备选方案：
- 为 section links 和 chips 再引入一档更亮的首页 CTA 蓝。拒绝原因是批准参考图更接近“先增强控件感和字重”，没有必要靠增加色盘复杂度来达成。

### Decision: 剩余视觉差距通过 country/topic/summary 三组卡片的局部密度微调收口
现在剩下的问题已经不再是全局文本角色分配，而是几组具体卡片在字号、字重和卡壳存在感上还差最后一档。因此最后这一轮只针对 country cards、topic cards 和 summary row 做局部加密处理，让它们更接近批准参考图的信息密度与决断感。

备选方案：
- 再次回头重调整页首页 token 层级。拒绝原因是最新截图对比已经说明，剩余偏差是局部卡片组问题，不是系统性层级错误。

### Decision: 原地替换 hero-stat 图标资产，保留现有 hero metric 结构和 CSS 挂载点
首页 hero 已经通过稳定的 `hero-*.svg` 资源引用渲染每个 stat icon。既然用户提供的是一组一一对应的替换素材，实现就应直接替换这六个资源文件，并继续沿用现有的 `hero-stat-icon--*` class 和 markup 结构。

备选方案：
- 把 hero stat cards 改写为内联 `<img>` 或新的 sprite 机制。拒绝原因是当前请求只是采用指定图稿，现有资源挂载方式已经足够完成替换。

### Decision: 把 topic-card 图标从内联 SVG path 切换为静态资产图片，同时保留现有卡片类名
首页 topic cards 当前通过 `homepage-topic-reference.mjs` 输出小型内联 SVG path。既然用户提供的是一组六个稳定 SVG 资产，而且其最新批准版本只对第 3 个图标做了额外加粗来改善页面观感，实现应把 topic icon renderer 切换为仓库内稳定资产路径下的 `<img>` 引用，同时继续保留 `topic-card-icon` 和 `topic-card-icon--*` 这组 class hooks。

备选方案：
- 把这组截图提取图标重新矢量化，再手写回新的内联 path。拒绝原因是源说明已经明确指出，从截图反推 path 会改变细节形状，这与用户想保留精确轮廓的目标相冲突。

### Decision: 除非验证暴露出生成依赖，否则保持 CSS-only
目标问题存在于首页样式层，而不是内容或生成 HTML 结构层。实现会尽量保持 CSS-only；只有在验证失败时，才补充必要的生成产物或测试夹具刷新。

备选方案：
- 在样式清理时预先重生成首页 HTML。拒绝原因是当前计划里没有任何变更需要修改 markup。

## Risks / Trade-offs

- [如果削弱蓝色强调过头，部分卡片可能会比批准参考图更“平”] -> 保留标题和实体标签的更强首页蓝，只把解释性文案移向更平静的 body/meta 角色。
- [统一 link color 可能会让少数之前更亮的 CTA 显得没那么跳] -> 保留统一默认 link role 和更深的 hover role，再优先通过字重、字号和局部 affordance 样式把强调度补回来，而不是继续增加颜色分叉。
- [响应式覆盖层里可能还残留旧的写死颜色] -> 在桌面角色收敛之后，顺带检查 tablet/mobile CSS 里是否还留着旧的文字颜色角色。
- [仓库里最近已经有多轮相邻首页 OpenSpec 变更] -> 把这次严格限制在文本颜色层级上，确保能和前面的 search、topic、map、stakeholder 改动平滑叠加。
- [把承载内容的短副信息重新抬回 body 可能会让真正的辅助信息又变得太响] -> 只把日期、placeholder 和极弱辅助标签留在 metadata，再结合批准截图核对结果，而不是只按 selector 名称机械归类。
- [局部密度微调可能过头，反而让白底卡片显得发重] -> 只做小幅加重，并且把范围严格限制在截图明确指出的三组卡片。
- [直接替换资源文件可能因为文件名映射错误而悄悄偏离用户提供的源素材] -> 保持一一对应的显式映射，并增加一条很窄的资源级验证，确认仓库内 hero icon 已带上预期的 V10 filled-path 特征。
- [把 topic icons 从内联 SVG 切到图片资源后，卡片内可能出现轻微对齐或尺寸漂移] -> 保留现有 icon class hooks，用当前固定 icon 盒子约束 `<img>`，并补一条很窄的渲染/断言检查，确认生成页引用了预期资源。

## Migration Plan

1. 在 OpenSpec 工件及中文配套文件中记录这个很窄的文本颜色一致性范围。
2. 在 `landing.base.css` 里整合首页白底区块的文本角色。
3. 更新首页模块 CSS，让它们使用共享文本角色而不是各自的一次性近似蓝色。
4. 对照截图，把当前被压得过轻的承载内容短文案从 metadata 重新提升到 body。
5. 通过排版和 border/shadow 处理强化共享 CTA 与控件感，同时保持同一套交互语言。
6. 对 country cards、topic cards 和 summary cards 做最后一轮局部密度微调，让文字和卡壳更贴近批准截图。
7. 直接用用户提供的 V10 素材替换六个 hero-stat SVG 资源文件，保留当前 hero 结构和 CSS 引用不变。
8. 把六个 topic-card 内联 icon 定义改为引用用户当前批准的 SVG 资产，放到仓库内稳定路径下，同时保持 topic card 布局和类名挂载点不变。
9. 运行与首页渲染和样式相关的最小必要验证，并补 hero-stat 与 topic-card 图标替换的窄资源级验证。
10. 如果结果把已批准的视觉平衡修得过头，就只回滚颜色角色分配，不动布局或内容工件。

## Open Questions

- None. 用户已经在评审之后明确同意按文本颜色一致性方案继续。
