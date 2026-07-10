## Why

当前 landing 首页在窄屏手机上有两类回归。在 `390px` 视口中，header 仍然显示桌面导航，多个首页区块继续沿用桌面网格，导致横向稳定性被破坏；在 `320x568` 视口中，hero 主 CTA 被推到首屏下方很远的位置，紧凑品牌标识的点击面偏小，stakeholder / summary 模块也仍然带着桌面密度。

这个后续修复需要现在落地，因为仓库最近刚把多个首页区块对齐到批准的桌面参考图，不能让这些桌面优化带着标准手机和小手机上的破版体验一起发布。

## What Changes

- 为 landing 首页新增一个同时覆盖手机与小手机宽度的布局稳定性变更。
- 更新共享 landing mobile CSS：header 隐藏桌面导航，启用现有紧凑移动端控件，确保品牌标识保持在 `44px` 级别的可点击范围内，并让 action 组对齐参考图里的窄屏 header 结构。
- 为窄屏 header action 组补上缺失的独立联系入口，让手机布局在不发生文字重叠的前提下同时暴露语言切换、联系和菜单控件。
- 在手机宽度下重排 hero，让 supporting copy、CTA 和 metrics 保持在同一条阅读轨道上，同时让 CTA 区块继续出现在 metric grid 之前，并进一步收紧小手机的间距与内边距，确保 `320x568` 下主 CTA 仍靠近首屏。
- 继续把 `decision-strip` 容器改成单列手机布局，但让 stakeholder 卡片在手机上采用更紧凑的双列排布，而不是单列长栈。
- 在手机宽度下，以能压过桌面区块规则的选择器优先级覆盖英文 `section-summary-modules` 网格，移除固定卡片高度假设，并在小手机上压缩 edition cover 的占位，但不把它塌成过高的单列卡片。
- 平滑小手机断点行为，让 `320px`、`360px` 和 `390px` 共享同一套 hero 阅读顺序与菜单/内容内边距，而不是在 `<=360px` 时切到第二套模板。
- 将首页专属的手机覆盖规则拆到独立 responsive partial 中，保证移动端行为可维护，同时不突破仓库的样式文件体积约束。
- 刷新 landing 页验证，断言手机宽度下的 header、hero、audience、summary 以及小手机规则都按预期生效。
- 保持已批准的桌面/平板布局、文案、路由，以及法文兼容首页结构不变，范围只限于窄屏覆盖规则。

## Capabilities

### New Capabilities
- `homepage-mobile-layout-stability`：landing 首页在手机宽度下保持稳定、可阅读且优先暴露主操作，通过切换到移动端导航控件、让小手机与标准手机共享同一套 hero 阅读顺序、让 CTA 先于密集指标出现，并把桌面过重的网格切换成适合手机的布局来实现。

### Modified Capabilities
- None.

## Impact

- 受影响的 landing 源生成：`scripts/shared/landing-shell.mjs`
- 受影响的 landing 样式：`assets/css/landing.header.css`、`assets/css/landing.responsive-mobile.css`、`assets/css/landing.responsive-mobile-homepage.css`、`assets/css/landing.css`
- 受影响的验证：`scripts/test-site-render.sh`
- 重建后会受影响的生成输出：`public/index.html`、`public/fr/index.html`，以及所有使用共享响应式样式表的 landing 变体
