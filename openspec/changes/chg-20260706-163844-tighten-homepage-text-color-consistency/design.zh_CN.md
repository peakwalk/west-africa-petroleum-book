## Context

当前 landing 样式已经在 `assets/css/landing.base.css` 里定义了一部分首页配色，包括 `--homepage-heading-text`、`--homepage-primary-text`、`--brand-blue` 和 `--brand-blue-deep`。但白底首页模块仍然额外混用了很多写死颜色，例如 `#17346f`、`#244da3`、`#2f56a4`、`#2f67f6`、`#4a5d78`、`#61708a` 和 `#7287b3`，而这些值承担的视觉角色其实非常接近。

这种漂移现在最明显地出现在 header navigation、stakeholder strip、country cards、search chips、topic cards 和收尾的 summary row 之间。批准过的首页信息架构和区块构成并不需要再次重做；真正的缺口是说明性文案看起来经常和交互文字一样强调，而不同交互元素之间也缺少一条清晰统一的 link color 基线。

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

### Decision: 除非验证暴露出生成依赖，否则保持 CSS-only
目标问题存在于首页样式层，而不是内容或生成 HTML 结构层。实现会尽量保持 CSS-only；只有在验证失败时，才补充必要的生成产物或测试夹具刷新。

备选方案：
- 在样式清理时预先重生成首页 HTML。拒绝原因是当前计划里没有任何变更需要修改 markup。

## Risks / Trade-offs

- [如果削弱蓝色强调过头，部分卡片可能会比批准参考图更“平”] -> 保留标题和实体标签的更强首页蓝，只把解释性文案移向更平静的 body/meta 角色。
- [统一 link color 可能会让少数之前更亮的 CTA 显得没那么跳] -> 保留统一默认 link role 和更深的 hover role，再在上下文中复查主要 CTA 是否仍然足够可点击。
- [响应式覆盖层里可能还残留旧的写死颜色] -> 在桌面角色收敛之后，顺带检查 tablet/mobile CSS 里是否还留着旧的文字颜色角色。
- [仓库里最近已经有多轮相邻首页 OpenSpec 变更] -> 把这次严格限制在文本颜色层级上，确保能和前面的 search、topic、map、stakeholder 改动平滑叠加。

## Migration Plan

1. 在 OpenSpec 工件及中文配套文件中记录这个很窄的文本颜色一致性范围。
2. 在 `landing.base.css` 里整合首页白底区块的文本角色。
3. 更新首页模块 CSS，让它们使用共享文本角色而不是各自的一次性近似蓝色。
4. 运行与首页渲染和样式相关的最小必要验证。
5. 如果结果把已批准的视觉平衡修得过头，就只回滚颜色角色分配，不动布局或内容工件。

## Open Questions

- None. 用户已经在评审之后明确同意按文本颜色一致性方案继续。
