## Why

当前 landing 构建会把整个 `assets/` 目录复制到 `public/assets/` 和 `public/fr/assets/`。这会把一批已经不再被 landing 生成脚本、landing 样式或已发布 landing 页面引用的历史图片也一并带进产物。它们没有任何当前运行时价值，却增加了仓库噪音，也让构建后的静态资源目录继续膨胀。

这次清理需要保持保守。只删除已经退役、且没有当前运行时契约的 landing 历史图片，同时保留仍然作为有效交付链路源文件的资源，包括 `assets/images/upstream-atlas-hero-book.png` 和 `assets/images/upstream-atlas-favicon.png`。

## What Changes

- 从 `assets/images/` 中删除一组保守确认过的、未被引用的 landing 历史图片。
- 刷新 landing 校验，让源目录和构建产物目录一旦重新出现这些退役文件就直接失败。
- 不改变当前仍在使用的 landing 图片契约，包括 WebP 导航 logo、首页 SVG 地图面板、首页 WebP 图书封面，以及 favicon 源文件链路。

## Capabilities

### New Capabilities
- `landing-unused-image-asset-cleanup`：landing 源目录和生成后的 public 资源目录都排除一组明确列出的退役历史图片文件。

### Modified Capabilities
- None.

## Impact

- 从 `assets/images/` 删除的源资源：
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
- 受影响的校验：`tests/test_public_editions.py`、`scripts/test-site-render.sh`
- 重建后受影响的生成产物：`public/assets/images/*`、`public/fr/assets/images/*`
