## ADDED Requirements

### Requirement: English homepage current-edition cover uses optimized non-critical delivery
英文 landing 首页 SHALL 用仓库内维护的优化版 WebP 封面资源渲染 current-edition 卡片，并 SHALL 把这张图片标记为非关键资源，避免它和首页 hero 争抢初始加载。

#### Scenario: English homepage cover card uses optimized WebP
- **WHEN** 英文 landing 首页渲染 current-edition summary card
- **THEN** 卡片图片引用 `assets/images/upstream-atlas-hero-book.webp`
- **AND** 卡片图片标记包含 `loading="lazy"`
- **AND** 卡片图片标记包含 `decoding="async"`
- **AND** 生成后的首页不会再为这个卡片引用 `assets/images/upstream-atlas-hero-book.png`
