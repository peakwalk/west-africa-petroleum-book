## ADDED Requirements

### Requirement: Landing 源目录排除退役历史图片变体
仓库 SHALL 把一组明确列出的退役 landing 图片变体排除在活动源目录之外，避免它们被站点构建再次发布。

#### Scenario: 退役 landing 源资源保持删除状态
- **WHEN** 检查 landing 源资源目录
- **THEN** `assets/images/` 下不存在以下文件：
  - `cover.png`
  - `homepage-west-africa-map-panel.png`
  - `homepage-west-africa-map-panel.webp`
  - `homepage-west-africa-map-panel@2x.png`
  - `prototype-hero-cutout.png`
  - `prototype-hero-edge-left.png`
  - `prototype-hero-edge-right.png`
  - `prototype-hero-grayscale-left.png`
  - `prototype-hero-grayscale-right.png`
  - `prototype-hero-overlay.png`
  - `upstream-atlas-hero-v2-photo.png`
  - `upstream-atlas-logo.png`
  - `upstream-atlas-nav-logo.png`

### Requirement: Landing 构建不再重新发布这些退役历史图片
landing 站点构建 SHALL 不把这些退役图片重新复制进英文或法文的 public 资源目录。

#### Scenario: 生成后的 landing 资源目录排除退役图片
- **WHEN** `npm run build:site` 完成
- **THEN** 这份退役图片清单不会出现在 `public/assets/images/`
- **AND** 同一份退役图片清单也不会出现在 `public/fr/assets/images/`
