## Context

landing 首页的结构标记其实已经有移动端菜单和紧凑品牌标识，但手机断点样式在几个关键区域里仍然表现得像桌面页。`390px` 下，header 继续显示桌面导航，`decision-strip` 继续保留桌面双列，英文 summary row 继续保留桌面四列；`320x568` 下，hero 指标区仍在 CTA 之前，紧凑品牌标识的点击面偏小，stakeholder / summary 模块也还带着桌面密度。

headless Playwright 截图给出的证据很具体：

- `390px`：`document.documentElement.scrollWidth` 扩大到 `477px`
- `390px`：`.decision-strip-inner` 和 `.decision-strip-copy` 仍然解析成双列
- `390px`：`.section-summary-modules .summary-grid` 仍然解析成四列
- `320x568`：hero 主 CTA 被推到了首屏很下方
- `320x568`：紧凑品牌标识的点击区域大约只有 `32x44`，低于期望的触达面

用户给的 header 参考图又增加了一个明确约束：窄屏 header 应该呈现为左对齐的紧凑品牌标识，加上右对齐的控制组，控制组由语言切换胶囊、圆形联系按钮和菜单胶囊组成。现有 landing CSS 已经有 `.header-contact-link`，因此最窄实现路径不是发明新模式，而是把这个缺失控件真正接进生成后的 header，并收紧手机断点行为。

仓库还要求 landing 样式文件保持可审阅的体量，所以最终方案不能继续把所有手机逻辑都堆进一个不断膨胀的 responsive 文件里。

## Goals / Non-Goals

**Goals:**
- 去掉 landing 首页在手机宽度下的横向溢出。
- 启用已经存在的移动端 header 导航方案，而不是在手机上继续显示桌面导航。
- 让手机 header 控制组对齐用户提供的参考图，包括独立联系按钮，以及不再出现品牌文字重叠。
- 让主 hero CTA 在手机宽度下出现在 metric grid 之前，在小手机上仍保持靠近首屏，并避免为 `<=360px` 单独切出第二套 hero 阅读顺序。
- 让 `decision-strip` 在手机宽度下干净地折叠，同时让 stakeholder 卡片保持足够紧凑，避免区块过高。
- 让英文 summary 区块在手机宽度下可读，不再继承桌面固定卡片高度。
- 补上回归检查，避免这些手机断点覆盖规则再次丢失。

**Non-Goals:**
- 不重做桌面或平板版 landing 体验。
- 不修改首页文案、路由或区块顺序。
- 不重做法文兼容首页主体结构，除非它自然受到共享 mobile CSS 的影响。
- 不重新打开 footer 布局问题，除非新的手机证据表明它仍在溢出。

## Decisions

### Decision: 在 `landing.responsive-mobile.css` 中保留共享手机基础规则，并把首页专属规则拆到独立 partial
现有标记已经暴露出需要的移动端 header 控件和区块包装器。可持续的修复方式，是把共享 header / 通用手机基础规则留在 `assets/css/landing.responsive-mobile.css`，同时把首页专属的手机行为拆到 `assets/css/landing.responsive-mobile-homepage.css`，这样既能修复问题，也能继续满足仓库对样式文件体量的约束。

备选方案：
- 直接补丁生成后的 `public/*.html`。拒绝，因为生成文件不是事实来源，下次构建会被覆盖。
- 把所有新增规则继续塞进同一个 responsive 文件。拒绝，因为 `landing.responsive-mobile.css` 会超过仓库允许的可审阅尺寸。

### Decision: summary grid 覆盖要匹配桌面选择器优先级
桌面 summary 布局来自 `.section-summary-modules .summary-grid`。因此手机端覆盖必须使用同样带区块限定的选择器，不能只写 `.summary-grid`，否则即便源顺序更靠后，桌面规则仍会继续生效。

备选方案：
- 给手机端 grid 规则加 `!important`。拒绝，因为直接匹配既有选择器优先级更干净，也更容易维护。

### Decision: 手机上复用平板已有的移动菜单显示模式
平板样式已经会隐藏 `.primary-nav` 并显示 `.header-actions` 与 `.mobile-nav-menu`。手机断点应该明确沿用这套行为，而不是再造第三种导航模式。

备选方案：
- 保留桌面导航，只继续压缩间距。拒绝，因为当前手机截图已经显示这些链接会把 header 挤乱，并加剧布局不稳定。

### Decision: 复用现有 header 联系按钮样式和现有邮件图形
landing 样式里已经定义了 `.header-contact-link`，reader toolbar 里也已经有与项目线性图标语言一致的邮件图形。最窄的修复方式，就是在 `scripts/shared/landing-shell.mjs` 中真正渲染这个联系入口，在手机断点隐藏品牌参考文字，并让 mobile 规则把右侧三个控件排成一个一致的 action 组。

备选方案：
- 新增一个只在手机上显示的文字版 Contact 胶囊。拒绝，因为参考图明确是圆形图标按钮，而且 header 宽度也比桌面文字 CTA 更紧。
- 继续把联系入口只放在下拉菜单里。拒绝，因为用户给的参考图要求它在顶栏第一行就可见。

### Decision: 通过 CSS 重排 hero，而不是改首页 DOM 顺序
hero copy block 的 DOM 结构已经稳定。对于手机来说，风险最小的做法是把 `.hero-copy-block-v2` 变成 flex column，让 supporting copy、CTA 和 metric grid 保持在同一条阅读轨道上，并让 CTA 区块出现在 metric grid 之前。到了小手机宽度，持久方案是继续收紧这条轨道的宽度与间距，而不是再引入第二套 hero 顺序。

备选方案：
- 直接改写 `scripts/shared/homepage-content.mjs` 中的标记顺序。拒绝，因为桌面和平板当前都依赖现有 DOM 顺序正常工作。

### Decision: 平滑小手机断点，而不是为 `<=360px` 分叉第二套移动模板
第一轮手机修复去掉了溢出，但后续对 `320x568` / `360x640` / `390x844` 的截图又暴露出新的断点跳变：`390px` 仍然是 copy 在 CTA 前，而 `360px` 却切成了 CTA-first hero；`320px` 下 copy/stat 区块又比 CTA 更靠右；mobile menu panel 的左右内边距不对称；Current Edition 卡片在封面下堆后也显得过空。可持续的修复方式，是让 `320px` 到 `390px` 共享同一套 hero 阅读顺序和内容内边距轨道，让 `.mobile-nav-panel` 对齐这套 gutter，并保留紧凑的 inline edition-card 布局。

备选方案：
- 保留 `<=360px` 的特殊 hero 顺序与封面下堆版式。拒绝，因为它会让相邻手机宽度之间出现明显结构跳变，也会在 summary 区块里浪费纵向空间。

### Decision: audience 卡片在手机上改成更紧凑的双列，而不是单列长栈
桌面端的六列 stakeholder row 不能原样保留，但如果手机上改成一列一张卡，会把这个区块拉得过高。双列手机网格配合弹性卡片尺寸，能在不牺牲可读性的前提下控制页面纵向长度。

备选方案：
- 保持单列手机栈。拒绝，因为它只会增加滚动深度，并不会提升理解效率。

## Risks / Trade-offs

- [手机专用选择器更新可能误伤平板宽度] -> 所有新增覆盖都限制在 `@media (max-width: 767px)` 或更窄断点中，同时保留 `landing.responsive-tablet.css` 里的平板行为。
- [summary grid 修复可能误伤法文兼容区块] -> 将单列覆盖限定在 `.section-summary-modules .summary-grid`，只命中英文 summary row。
- [header 控件切换若不完整，可能导致导航被整体隐藏] -> 扩展验证，断言手机 header 代码块里同时存在“隐藏桌面导航”和“显示移动端控件”的规则。
- [CTA 优先级调整可能让 hero 信息被隐藏] -> 保留所有 hero 文案；小手机只收紧间距与 gutter，不切换成另一套 hero 模板。
