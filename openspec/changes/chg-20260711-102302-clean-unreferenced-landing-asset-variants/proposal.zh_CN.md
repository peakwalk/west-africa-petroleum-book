## Why

landing 资源树里还留着一组历史图片变体。它们已经不再被生成后的 landing HTML、生成后的 landing CSS，或当前 book shell 引用。但由于 `scripts/build_site.mjs` 会把整个 `assets/` 目录复制到英文和法文两个 public 输出目录，这批死资源仍会继续随构建产物一起发布。

这次清理继续保持保守，并且明确不碰当前 book theme 仍在使用的那条资源链。尤其不动活跃的 `prototype-hero-graywhite-*.webp`，也不动它们保留下来的 PNG 源备份。

## What Changes

- 从 `assets/images/` 中删除第二批已经无引用的历史 landing 图片变体。
- 更新 landing 校验，让源目录和 public 产物目录在这些变体回归时直接失败。
- 保持当前 landing 和 book-theme 的有效资源契约不变。

## Capabilities

### New Capabilities
- `landing-unreferenced-asset-variant-cleanup`：landing 源目录和生成后的 public 资源目录排除一组已经不属于任何运行时契约的历史图片变体。

### Modified Capabilities
- None.

## Impact

- 从 `assets/images/` 删除的源资源：
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
- 受影响的校验：`tests/test_public_editions.py`、`scripts/test-site-render.sh`
- 重建后受影响的生成产物：`public/assets/images/*`、`public/fr/assets/images/*`
