## 1. OpenSpec 与回归范围

- [x] 1.1 补齐首页 mobile 布局稳定性变更的 proposal、design、spec 及中文配套文件。

## 2. Landing 手机布局修复

- [x] 2.1 补上 landing 验证检查：当手机宽度下 header 仍显示桌面导航，或关键区块网格不再堆叠时，检查必须失败。
- [x] 2.2 更新共享 header/mobile 响应式样式，让手机 header 以紧凑品牌触达面暴露语言、联系和菜单控件，并贴近用户给出的参考 header 布局。
- [x] 2.3 增加首页专属手机覆盖：让 hero CTA 先于 metric grid 出现，让 stakeholder 卡片改成更紧凑的双列手机网格，并移除 summary 模块的桌面高度假设。
- [x] 2.4 把首页专属手机覆盖拆到独立 responsive partial 中，确保仓库的样式文件体积约束继续成立。
- [x] 2.5 平滑小手机断点，让 `320px`、`360px` 和 `390px` 共享同一套 hero 阅读顺序、对齐后的菜单内边距，以及更紧凑的 Current Edition 卡片。

## 3. 重建与验证

- [x] 3.1 重建站点，并运行针对这些手机断点规则的最小 landing 验证命令。
- [x] 3.2 以 `390px` 宽度和 `320x568` 小手机尺寸重新运行 headless Playwright 截图，确认首页不再出现横向溢出，且主 CTA 仍靠近首屏。
- [x] 3.3 以 `320x568`、`360x640` 和 `390x844` 重新运行 headless Playwright 截图，确认小手机的 gutter 已对齐，且不再出现断点顺序跳变。
