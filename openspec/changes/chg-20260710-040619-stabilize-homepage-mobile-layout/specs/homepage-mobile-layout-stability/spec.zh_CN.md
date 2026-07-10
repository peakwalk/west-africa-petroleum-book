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
- **WHEN** 英文 landing 首页在不大于 `767px` 的手机宽度下渲染
- **THEN** `.section-summary-modules .summary-grid` 使用单列布局
- **THEN** summary 卡片保持可读，不出现裁切或横向滚动

#### Scenario: Hero CTA appears before dense metrics on phones
- **WHEN** landing 首页在不大于 `767px` 的手机宽度下渲染
- **THEN** hero 主 CTA 区块出现在 hero metric grid 之前
- **THEN** hero metric grid 折叠为适合手机的多行布局

#### Scenario: Phone audience cards keep dense readable layout
- **WHEN** landing 首页在不大于 `767px` 的手机宽度下渲染
- **THEN** stakeholder 卡片以更紧凑的双列手机网格渲染
- **THEN** 这些卡片不再依赖会导致溢出或过长滚动的桌面固定宽度尺寸

#### Scenario: Compact phones keep the CTA and edition card readable
- **WHEN** landing 首页在不大于 `360px` 的小手机宽度下渲染
- **THEN** supporting copy、主 CTA 和 hero metric grid 保持在同一条内缩内容轨道上，同时 CTA 继续出现在密集指标区之前
- **THEN** 通过更紧的间距让主 hero CTA 仍保持靠近首屏，而不是切换成一套与相邻手机宽度不同的 hero 阅读顺序
- **THEN** edition card 保持紧凑的文字加封面并排布局，避免在窄视口里出现过多空白高度
