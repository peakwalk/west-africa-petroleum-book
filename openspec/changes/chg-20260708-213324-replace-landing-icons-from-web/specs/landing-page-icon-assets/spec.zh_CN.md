## ADDED Requirements

### Requirement: Landing pages use consistent web-sourced SVG icon assets outside hero stats
生成后的 landing pages 在保留当前 `hero-stat-icon` 资源不变的前提下，必须让其余可见图标位统一使用来自同一个官方在线图标库的 SVG 资源。

#### Scenario: English homepage topic cards use SVG assets
- **WHEN** 生成英文首页时
- **THEN** 每个 topic-reference 卡片必须引用 `/assets/icons/topics/*.svg`，而不是 `/assets/icons/topics/*.png`

#### Scenario: Shared non-hero landing icon surfaces use curated SVG assets
- **WHEN** 生成英文首页或法语兼容首页时
- **THEN** stakeholder 图标、search-scope 图标、homepage feature 图标、audience 图标、country-signal 图标以及 control sprite 图标都必须解析到现有 landing 资源目录下的 SVG 资产
