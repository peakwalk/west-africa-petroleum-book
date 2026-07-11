## ADDED Requirements

### Requirement: Landing 源目录排除无引用历史资源变体
仓库 SHALL 把一组无引用的历史 landing 资源变体排除在活动源目录之外，同时保留仍在使用的 graywhite book-theme 资源。

#### Scenario: 无引用历史源资源保持删除状态
- **WHEN** 检查 landing 源资源目录
- **THEN** `assets/images/` 下不存在以下文件：
  - `homepage-cabo-verde-inset.svg`
  - `prototype-hero-dusk.webp`
  - `prototype-hero-night.webp`
  - `prototype-hero-sunset-right.webp`
  - `prototype-hero-sunset-source.webp`
  - `prototype-hero.jpg`
  - `upstream-atlas-hero-v2-photo-right-fade.webp`
  - `upstream-atlas-hero-v3-clean.webp`
  - `upstream-atlas-hero-v4-clean.webp`
  - `upstream-atlas-hero-v5-soft-left.webp`
  - `upstream-atlas-hero-v6-soft-left.webp`
  - `upstream-atlas-wordmark.png`
  - `west-africa-intelligence-overlay.svg`

### Requirement: Landing 构建不再重新发布无引用历史资源变体
landing 站点构建 SHALL 不把这些无引用历史资源变体重新复制进英文或法文 public 资源目录。

#### Scenario: 生成后的 landing 资源目录排除无引用变体
- **WHEN** `npm run build:site` 完成
- **THEN** 这份无引用历史资源清单不会出现在 `public/assets/images/`
- **AND** 同一份清单也不会出现在 `public/fr/assets/images/`
