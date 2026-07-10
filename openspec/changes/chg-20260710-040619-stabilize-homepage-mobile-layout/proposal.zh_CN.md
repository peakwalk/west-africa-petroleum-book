## Why

当前 landing 首页在窄屏手机上有两类回归。在 `390px` 视口中，header 仍然显示桌面导航，多个首页区块继续沿用桌面网格，导致横向稳定性被破坏；在 `320x568` 视口中，hero 主 CTA 被推到首屏下方很远的位置，紧凑品牌标识的点击面偏小，stakeholder / summary 模块也仍然带着桌面密度。后续在 `768x1024` 的复审里还暴露出一层混合态：顶部仍是紧凑控件，但 hero CTA 又退回到 metric grid 之后，并缩成了行内按钮。第一轮补桥之后，同样的 `768x1024` 复审仍然视觉上不对，因为页面看起来更像被放大的手机布局：CTA 横条过满，audience 网格中间留出过大的空白。再往 `1023px` 与 `1024px` 边界复审时，又出现了新的混合态：`1023px` 仍然是平板 header 控件，但 hero / action 密度已经提前向桌面漂移；`1024px` 则在首页其他区块切回桌面密度后，summary 还停留在平板双列状态。最新一轮窄屏评审又补充出 3 个仍需收口的小问题：`320px` hero 标题仍然过于贴近右边界，`767px` 这个手机上边界仍然因为单列内容网格而显得过于稀疏，`861px` 到 `1119px` 的 hero 操作轨道在平板上界附近开始出现明显的左重心。

这个后续修复需要现在落地，因为仓库最近刚把多个首页区块对齐到批准的桌面参考图，不能让这些桌面优化带着标准手机和小手机上的破版体验一起发布。

## What Changes

- 为 landing 首页新增一个同时覆盖手机与小手机宽度的布局稳定性变更。
- 更新共享 landing mobile CSS：header 隐藏桌面导航，启用现有紧凑移动端控件，确保品牌标识保持在 `44px` 级别的可点击范围内，并让 action 组对齐参考图里的窄屏 header 结构。
- 为窄屏 header action 组补上缺失的独立联系入口，让手机布局在不发生文字重叠的前提下同时暴露语言切换、联系和菜单控件。
- 在手机宽度下重排 hero，让 supporting copy、CTA 和 metrics 保持在同一条阅读轨道上，同时让 CTA 区块继续出现在 metric grid 之前，并进一步收紧小手机的间距与内边距，确保 `320x568` 下主 CTA 仍靠近首屏。
- 新增 `768px` 到 `860px` 的竖屏平板过渡层，让平板 header 保持当前处理方式，同时让 hero 继续沿用已批准的窄屏“CTA 先于 metrics”阅读优先级，但整体改成更克制的内容轨道、更紧凑的 `3 x 2` 指标网格，以及更贴近平板密度的 `3 x 2` audience 网格，而不是沿用放大的手机式满宽布局。
- 新增 `861px` 到 `1119px` 的宽平板过渡层，让紧凑平板 header 控件继续与平板密度的 hero、audience、topics、countries 和 summary 网格配套，而不是在 `1024px` 左右再次落入平板/桌面混合态。
- 将 landing 小桌面 header 的起始点从 `1024px` 延后到 `1120px`，让桌面导航、logo 间距和高密度区块网格同时切换。
- 避免首页 summary modules 在 `1119px` 及以下宽度继续停留在桌面四列布局里，改成双列平板布局，并让卡片高度跟随内容而不是继续被桌面等高规则拉伸。
- 新增 `700px` 到 `767px` 的大手机过渡层，让首页内容网格在进入平板 header 模式之前先收敛成双列，减少手机上界到平板下界之间过于生硬的密度跳变。
- 新增一个 `<=320px` 的 hero 标题微调层，让小手机标题重新获得可见的右侧安全边距，同时不打乱已经稳定的 copy / CTA 轨道。
- 让 `861px` 到 `1119px` 的 hero 内容轨道从固定宽度改成更流体的宽度策略，使宽平板仍然保持平板阅读顺序，但不会在 `1119px` 附近显得明显左重。
- 继续把 `decision-strip` 容器改成单列手机布局，但让 stakeholder 卡片在手机上采用更紧凑的双列排布，而不是单列长栈。
- 在手机宽度下，以能压过桌面区块规则的选择器优先级覆盖英文 `section-summary-modules` 网格，移除固定卡片高度假设，并在小手机上压缩 edition cover 的占位，但不把它塌成过高的单列卡片。
- 平滑小手机断点行为，让 `320px`、`360px` 和 `390px` 共享同一套 hero 阅读顺序与菜单/内容内边距，而不是在 `<=360px` 时切到第二套模板。
- 将首页专属的手机覆盖规则拆到独立 responsive partial 中，保证移动端行为可维护，同时不突破仓库的样式文件体积约束。
- 刷新 landing 页验证，断言手机宽度下的 header、hero、audience、summary 以及小手机规则都按预期生效。
- 保持已批准的桌面/平板布局、文案、路由，以及法文兼容首页结构不变，范围只限于窄屏覆盖规则。

## Capabilities

### New Capabilities
- `homepage-mobile-layout-stability`：landing 首页在小手机、标准手机、窄竖屏平板和宽平板过渡宽度下保持稳定、可阅读且优先暴露主操作，通过切换到移动端导航控件、让相邻窄屏宽度共享同一套 hero 阅读顺序、让 CTA 先于密集指标出现，并在真正进入桌面断点前把桌面过重的网格切换成适合手机或平板的布局来实现。

### Modified Capabilities
- None.

## Impact

- 受影响的 landing 源生成：`scripts/shared/landing-shell.mjs`
- 受影响的 landing 样式：`assets/css/landing.header.css`、`assets/css/landing.responsive-mobile.css`、`assets/css/landing.responsive-mobile-homepage.css`、`assets/css/landing.responsive-tablet.css`、`assets/css/landing.css`
- 受影响的验证：`scripts/test-site-render.sh`
- 重建后会受影响的生成输出：`public/index.html`、`public/fr/index.html`，以及所有使用共享响应式样式表的 landing 变体
