## ADDED Requirements

### Requirement: Landing homepage MUST remain stable and action-prioritized at phone widths
landing 首页在手机宽度下 SHALL 避免横向溢出，并 SHALL 优先暴露主阅读 CTA；当桌面布局会超出视口时，它必须把共享 header 和首页区块网格切换到适合手机的布局。

#### Scenario: Phone header switches to compact navigation controls
- **WHEN** landing 首页在不大于 `767px` 的手机宽度下渲染
- **THEN** 桌面 `.primary-nav` 被隐藏
- **THEN** 现有的 `.header-actions` 和 `.mobile-nav-menu` 控件可见
- **THEN** 紧凑品牌标识保持在视口内可见，且不再与品牌参考文字发生重叠
- **THEN** header action 行在语言切换与菜单控件之间显示一个独立的联系图标按钮
- **THEN** 小手机上的菜单面板与窄屏 header 其他控件使用同一套内缩 gutter 对齐

#### Scenario: Decision strip stacks on phones
- **WHEN** landing 首页在不大于 `767px` 的手机宽度下渲染
- **THEN** `.decision-strip-inner` 使用单列布局
- **THEN** `.decision-strip-copy` 使用单列布局
- **THEN** 该区块不再强制产生横向滚动

#### Scenario: English summary modules stack on phones
- **WHEN** 英文 landing 首页在不大于 `699px` 的手机宽度下渲染
- **THEN** `.section-summary-modules .summary-grid` 使用单列布局
- **THEN** summary 卡片保持可读，不出现裁切或横向滚动

#### Scenario: Large phones condense homepage content grids before tablet mode
- **WHEN** landing 首页在 `700px` 到 `767px` 的宽度下渲染
- **THEN** 紧凑手机 header 处理继续保持激活
- **THEN** countries、topics 和 summary 模块收敛成双列网格
- **THEN** 页面不再把过于稀疏的单列内容密度一直拖到平板断点

#### Scenario: English summary modules condense on tablets
- **WHEN** 英文 landing 首页在 `768px` 到 `1119px` 的宽度下渲染
- **THEN** `.section-summary-modules .summary-grid` 使用双列布局
- **THEN** 这组 summary 卡片不再停留在桌面四列并排的布局里
- **THEN** summary 卡片按内容高度对齐，不再继续被桌面最小高度假设拉伸

#### Scenario: Hero CTA appears before dense metrics on phones
- **WHEN** landing 首页在不大于 `767px` 的手机宽度下渲染
- **THEN** hero 主 CTA 区块出现在 hero metric grid 之前
- **THEN** hero metric grid 折叠为适合手机的多行布局

#### Scenario: Tablet portrait keeps the CTA ahead of dense metrics
- **WHEN** landing 首页在 `768px` 到 `860px` 的竖屏平板宽度下渲染
- **THEN** hero 标题、supporting copy、主 CTA 和 hero metric grid 保持在同一条纵向阅读轨道上
- **THEN** hero 主 CTA 区块出现在 hero metric grid 之前
- **THEN** CTA 保持在更克制的平板宽度操作轨道上，而不是像手机横条一样拉满整条内容宽度
- **THEN** hero metric grid 收敛成更紧凑的 `3 x 2` 竖屏平板布局
- **THEN** audience stakeholder 卡片收敛成更紧凑的 `3 x 2` 竖屏平板布局，不再在中间留下过大的空白带

#### Scenario: Wide tablets keep one coherent tablet-density layout
- **WHEN** landing 首页在 `861px` 到 `1119px` 的宽度下渲染
- **THEN** 紧凑平板 header 控件继续保持激活，而不是切换回桌面导航
- **THEN** hero 标题、supporting copy、主 CTA 和 hero metric grid 继续保持在同一套平板密度阅读轨道上
- **THEN** hero 主 CTA 继续保持整行平板操作条，而不是退回桌面式行内按钮
- **THEN** hero copy 与操作轨道可以随视口适度增长，而不是被锁死在单一固定宽度
- **THEN** hero metric grid 与 audience stakeholder 卡片继续保持更紧凑的 `3 x 2` 平板布局
- **THEN** topics、countries 和 summary 区块继续保持双列平板网格

#### Scenario: Desktop layout resumes together at `1120px`
- **WHEN** landing 首页在不小于 `1120px` 的宽度下渲染
- **THEN** 桌面 `.primary-nav` 可见
- **THEN** 紧凑平板 header 控件不再作为主要导航处理
- **THEN** 桌面密度的 hero 和各区块网格作为同一次切换恢复，而不是在 `1024px` 左右由不同模块各自切换

#### Scenario: Phone audience cards keep dense readable layout
- **WHEN** landing 首页在不大于 `767px` 的手机宽度下渲染
- **THEN** stakeholder 卡片以更紧凑的双列手机网格渲染
- **THEN** 这些卡片不再依赖会导致溢出或过长滚动的桌面固定宽度尺寸

#### Scenario: Compact phones keep the CTA and edition card readable
- **WHEN** landing 首页在不大于 `360px` 的小手机宽度下渲染
- **THEN** supporting copy、主 CTA 和 hero metric grid 保持在同一条内缩内容轨道上，同时 CTA 继续出现在密集指标区之前
- **THEN** 通过更紧的间距让主 hero CTA 仍保持靠近首屏，而不是切换成一套与相邻手机宽度不同的 hero 阅读顺序
- **THEN** edition card 保持紧凑的文字加封面并排布局，避免在窄视口里出现过多空白高度
- **THEN** `320px` 下的 hero 标题重新获得可见的右侧安全边距，而不是继续压向视口边缘
