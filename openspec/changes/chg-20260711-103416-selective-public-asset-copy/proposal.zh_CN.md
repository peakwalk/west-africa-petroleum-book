## Why

当前站点构建会把整个 `assets/` 目录同时复制到 `public/assets/` 和 `public/fr/assets/`，但这两个输出树实际并不需要同一套运行时资源。这个行为会把 `upstream-atlas-hero-book.png` 这类 source-only 图片重新发布，把只属于英文首页的资源带进法文站点树，也会把与当前 locale 无关的图标组继续塞进从不引用它们的输出目录。

下一步应该在不改页面 markup 和 theme 行为的前提下，继续缩减交付体积。最稳妥的方式，是把整树复制改成显式的 public 资源清单：保留当前运行时契约，排除 source-only 文件和 locale 无关文件。

## What Changes

- 在 `scripts/build_site.mjs` 中用显式资源清单替换整棵 public 资源复制。
- 保留英文和法文输出都需要的共享运行时资源。
- 把只属于英文首页的资源限制在 `public/assets/`，不再复制到 `public/fr/assets/`。
- 停止把 source-only 图片复制进任一 public 资源树。
- 停止把英文根输出里那些生成页面完全不引用的 icon 目录继续复制进去。

## Capabilities

### New Capabilities
- `selective-public-asset-copy`：站点构建只发布每个输出树真正需要的运行时资源子集，而不再复制整棵源资源树。

### Modified Capabilities
- `landing-site-build`：public 站点构建在保持现有页面行为不变的前提下，按 locale 缩减复制出来的资源面。

## Impact

- 受影响的构建逻辑：`scripts/build_site.mjs`
- 受影响的校验：`scripts/test-site-render.sh`
- 重建后受影响的生成产物：
  - `public/assets/**`
  - `public/fr/assets/**`
- 明确不再复制的关键资源：
  - `public/assets/images/upstream-atlas-hero-book.png`
  - `public/assets/images/prototype-hero-graywhite-left.png`
  - `public/assets/images/prototype-hero-graywhite-right.png`
  - `public/assets/icons/country-flags.svg`
  - `public/assets/icons/homepage/*`
  - `public/assets/icons/stakeholders/*`
  - `public/assets/icons/topics/*`
  - `public/fr/assets/images/upstream-atlas-hero-book.webp`
  - `public/fr/assets/images/homepage-west-africa-map-panel.svg`
  - `public/fr/assets/icons/homepage-cropped/*.webp`
  - `public/fr/assets/icons/homepage/hero-*.svg`
  - `public/fr/assets/icons/homepage/icon-close.svg`
  - `public/fr/assets/icons/homepage/icon-menu.svg`
  - `public/fr/assets/icons/homepage/icon-start-reading.svg`
  - `public/fr/assets/icons/homepage/icon-production.svg`
  - `public/fr/assets/icons/homepage/icon-exploration.svg`
  - `public/fr/assets/icons/homepage/icon-fiscal.svg`
  - `public/fr/assets/icons/homepage/icon-regulation.svg`
