## 1. OpenSpec 与回归范围

- [x] 1.1 补齐首页 mobile 布局稳定性变更的 proposal、design、spec 及中文配套文件。

## 2. Landing 手机布局修复

- [x] 2.1 补上 landing 验证检查：当手机宽度下 header 仍显示桌面导航，或关键区块网格不再堆叠时，检查必须失败。
- [x] 2.2 更新共享 header/mobile 响应式样式，让手机 header 以紧凑品牌触达面暴露语言、联系和菜单控件，并贴近用户给出的参考 header 布局。
- [x] 2.3 增加首页专属手机覆盖：让 hero CTA 先于 metric grid 出现，让 stakeholder 卡片改成更紧凑的双列手机网格，并移除 summary 模块的桌面高度假设。
- [x] 2.4 把首页专属手机覆盖拆到独立 responsive partial 中，确保仓库的样式文件体积约束继续成立。
- [x] 2.5 平滑小手机断点，让 `320px`、`360px` 和 `390px` 共享同一套 hero 阅读顺序、对齐后的菜单内边距，以及更紧凑的 Current Edition 卡片。
- [x] 2.6 增加 `768px`-`860px` 的竖屏平板过渡层，让 hero 在不破坏已批准平板 header 处理的前提下继续保持 CTA 先于密集指标。
- [x] 2.7 继续收口 `768px`-`860px` 的竖屏平板过渡层，让 hero 和 audience 区块呈现出更像平板的克制宽度与更紧凑的 `3 x 2` 网格，而不是放大的手机布局。
- [x] 2.8 增加一层带区块限定的 summary-module 平板覆盖到 `1119px`，让首页这组 summary 卡片折叠成两列，并去掉桌面等高假设。
- [x] 2.9 增加 `861px`-`1119px` 的宽平板过渡层，并把 landing 小桌面起始点后移到 `1120px`，让 header 控件、hero 密度、summary 卡片和后续区块网格不再在 `1023px` / `1024px` 附近各自切换。
- [x] 2.10 增加 `700px`-`767px` 的大手机过渡层，让首页内容网格在进入平板模式前先收敛成双列。
- [x] 2.11 增加一个 `<=320px` 的 hero 标题微调层，让小手机标题重新获得安全的右侧边距。
- [x] 2.12 让 `861px`-`1119px` 的 hero 轨道轻微流体化，使宽平板在 `1119px` 附近仍然保持均衡重心。
- [x] 2.13 统一首页 search field 在手机、平板和 small desktop 下的 gutter，让输入框在 `768px`-`1200px` 这一整段都不再呈现贴边观感。
- [x] 2.14 把 `861px`-`1119px` 的首页 search-scope chips 改成固定两行网格，让 `1119px` 宽平板不再在最后一行留下单独一个孤儿 chip。
- [x] 2.15 把基于内容宽度换行的 search-scope chips 改成稳定的响应式栅格：手机固定 `2` 列，大手机到 small desktop 固定 `4` 列，只有在 `1280px+` 真正放得下一行时才恢复单行布局。
- [x] 2.16 放宽 `1120px`-`1279px` 的首页 search-scope grid，让最长的 chip 标签在进入 `1280px+` 单行桌面布局之前也能回到单行显示。
- [x] 2.17 把原先 `700px`-`1119px` 的 search-scope 过渡层拆成 `700px`-`959px` 的 `2` 列布局和 `960px`-`1279px` 的加宽 `4` 列布局，让平板宽度不再强迫 chip 内部标签换行。
- [x] 2.18 继续把 `700px`-`959px` 的 search-scope 过渡层收口成居中的 `3` 列换行布局，让 `700px` 和 `768px` 更紧凑，同时保持最后一行视觉居中。
- [x] 2.19 删除已经被后续规则覆盖的 search-scope 重叠 media block，让最终断点逻辑只保留手机块、`3` 列过渡块和加宽 `4` 列过渡块。
- [x] 2.20 继续放宽 `700px`-`959px` 的 `3` 列 search-scope 容器，让这组 chips 在过渡段上边界附近更贴近 search input 的宽度。
- [x] 2.21 把 `700px`-`959px` 的 search-scope 过渡层再拆成 `700px`-`767px` 和 `768px`-`959px` 两段宽度规则，让 chips 组在平板断点前后都直接跟随 search input 的左右 gutter。
- [x] 2.22 继续放宽 `960px`-`1279px` 的 `4` 列 search-scope grid 上限，让宽平板和接近桌面的视口不再在更宽的 search input 下留下过于悬空的 chips 区块。
- [x] 2.23 把 `4` 列 search-scope 过渡层继续延伸到 `1439px`，并保持与 search input 同一内容宽度，让等宽双行区块只在真正的宽桌面区间才交接给单行 pills。
- [x] 2.24 把剩余的宽桌面增强态统一后移到 `1600px+`，让 `1440px` 不再同时触发 header、hero stat rail 和 search-scope 的复合跳变。
- [x] 2.25 删除会在 `1600px+` 反向压小 hero/decision-strip 的 override，并把剩余的 header/search-scope 宽桌面 handoff 再后移到 `1680px`，让 `1600px` 不再引入新的复合跳变。
- [x] 2.26 轻微放宽 `861px`-`1119px` hero 标题的排版宽度，让宽平板不再把 `Reference` 挤成第三行孤儿行，同时保留单列 tablet hero 的处理方式。

## 3. 重建与验证

- [x] 3.1 重建站点，并运行针对这些手机断点规则的最小 landing 验证命令。
- [x] 3.2 以 `390px` 宽度和 `320x568` 小手机尺寸重新运行 headless Playwright 截图，确认首页不再出现横向溢出，且主 CTA 仍靠近首屏。
- [x] 3.3 以 `320x568`、`360x640` 和 `390x844` 重新运行 headless Playwright 截图，确认小手机的 gutter 已对齐，且不再出现断点顺序跳变。
- [x] 3.4 以 `767px`、`768px` 和 `769px` 宽度重新运行 headless Playwright 截图，确认竖屏平板过渡层消除了断点跳变，同时没有回归平板 header 控件。
- [x] 3.5 以 `768px` 和 `860px` 宽度重新运行 headless Playwright 截图，确认收口后的竖屏平板布局保留了更克制的 CTA 轨道，并将指标区与 audience 区压缩为更紧凑的 `3 x 2` 网格。
- [x] 3.6 在 `1024px` 左右重新运行一次 headless Playwright 截图，确认首页 summary 卡片已经从四列收敛到两列。
- [x] 3.7 以 `860px`、`861px`、`1023px`、`1024px` 和 `1120px` 重新运行 headless 边界截图，确认新的宽平板过渡层消除了混合态，并且桌面起始点已在 `1120px` 统一生效。
- [x] 3.8 以 `320px`、`700px`、`767px`、`861px` 和 `1119px` 重新运行 headless 断点截图，确认标题右边距、大手机密度过渡层以及宽平板流体 hero 轨道都按预期生效。
- [x] 3.9 在跨断点 gutter 收口后重建站点，并重新运行最小化的首页 search-surface CSS 断言。
- [x] 3.10 去掉 `1119px` 孤儿 chip 行之后，重建站点并重新运行最小化的宽平板 search-scope CSS 断言。
- [x] 3.11 以 `320px`、`390px`、`700px`、`768px`、`1119px`、`1200px` 和 `1280px` 重新运行 headless search-scope 截图，确认 chips 栅格在恢复单行桌面布局之前都保持对齐。
- [x] 3.12 以 `1119px`、`1120px`、`1200px`、`1279px` 和 `1280px` 重新运行 headless search-scope 截图，确认放宽后的 small-desktop grid 消除了 chip 内部标签换行，同时仍保留居中的左右 gutter。
- [x] 3.13 以 `700px`、`768px`、`959px`、`960px`、`1024px`、`1119px` 和 `1280px` 重新运行 headless search-scope 截图，确认新的 `2` 列 / `4` 列断点拆分消除了平板换行，同时没有重新引入孤儿行或贴边 gutter。
- [x] 3.14 以 `700px`、`768px`、`959px` 和 `960px` 重新运行 headless search-scope 截图，确认居中的 `3` 列过渡层保持了单行标签，并在断点切换前后让最后一行维持居中。
- [x] 3.15 删除已废弃的 search-scope media block 后，重新运行 landing CSS 断言，确认精简后的样式表仍然解析到同一套已验证断点。
- [x] 3.16 放宽 `3` 列过渡层后，重新运行 `700px`、`768px` 和 `959px` 的 headless search-scope 截图，确认 chips 组更贴近 search input 宽度，同时没有重新引入标签换行。
- [x] 3.17 按 search input gutter 对齐拆分后的过渡层后，重新运行 `700px`、`768px` 和 `959px` 的 headless search-scope 截图，确认 chips 组与 input 共享同一侧边距，同时不破坏 `3` 列标签的单行显示。
- [x] 3.18 放宽 `4` 列上限后，重新运行 `960px`、`1024px`、`1119px` 和 `1279px` 的 headless search-scope 截图，确认更宽的平板区块减弱了居中悬空感，同时没有重新引入标签换行或孤儿行。
- [x] 3.19 把单行交接点移到宽桌面后，重新运行 `1279px`、`1280px`、`1366px`、`1439px` 和 `1440px` 的 headless search-scope 截图，确认断点跳变被收平，同时没有重新引入标签换行。
- [x] 3.20 把剩余的宽桌面增强态后移后，重新运行 `1439px`、`1440px` 和 `1600px` 的 headless landing 截图，确认 header、hero stat rail 和 search-scope 不再在 `1440px` 一起跳变。
- [x] 3.21 删除 shrinking override 并把最后一次 handoff 移到 `1680px` 后，重新运行 `1599px`、`1600px`、`1679px` 和 `1680px` 的 headless landing 截图，确认宽桌面过渡保持单调，不再在 `1600px` 同时改动多个区域。
- [x] 3.22 放宽宽平板 hero 标题宽度后，重新运行 `861px`、`959px`、`1119px` 和 `1120px` 的 headless landing 截图，确认孤儿行在 desktop onset 前消失，同时不重新引入此前的断点跳变。
