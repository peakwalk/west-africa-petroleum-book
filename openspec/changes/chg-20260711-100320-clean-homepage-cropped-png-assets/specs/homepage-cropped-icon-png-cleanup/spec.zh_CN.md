## ADDED Requirements

### Requirement: Homepage cropped icon 源目录排除退役 PNG 变体
仓库 SHALL 把退役的 `assets/icons/homepage-cropped/*.png` 变体排除在活动源目录之外，同时继续交付对应的 WebP 图标集。

#### Scenario: Cropped icon PNG 源文件保持删除状态
- **WHEN** 检查 homepage cropped-icon 源目录
- **THEN** `assets/icons/homepage-cropped/` 下不存在以下文件：
  - `icon-audience-operators.png`
  - `icon-audience-policy.png`
  - `icon-audience-research.png`
  - `icon-exploration.png`
  - `icon-fiscal.png`
  - `icon-industry-monitoring.png`
  - `icon-intelligence.png`
  - `icon-production.png`
  - `icon-regulation.png`
  - `icon-research.png`

### Requirement: Landing 构建不再重新发布 cropped icon PNG 变体
landing 站点构建 SHALL 不把这些退役 cropped-icon PNG 重新复制进英文或法文 public 资源目录。

#### Scenario: 生成后的 cropped-icon 资源目录排除 PNG 变体
- **WHEN** `npm run build:site` 完成
- **THEN** 这份退役 cropped-icon PNG 清单不会出现在 `public/assets/icons/homepage-cropped/`
- **AND** 同一份 PNG 清单也不会出现在 `public/fr/assets/icons/homepage-cropped/`
