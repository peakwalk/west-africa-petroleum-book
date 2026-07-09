## Why

当前 landing page 在英文首页和法语兼容首页上仍混用了多组历史图标资源。虽然部分区域已经使用 SVG 容器，但实际渲染的素材来源、图形语义和清晰度并不统一，而且英文 topic reference 卡片目前仍然引用 PNG，而不是 SVG。

用户现在已经明确提供了一套 26 个 SVG 文件，并要求 landing page 中对应的 26 个图标位使用这些文件。这个改动应当尽量收敛，只替换这些可映射资源，不改动 landing page 的文案和结构。

## What Changes

- 用 `/Users/edison/Downloads/Project - Africa_Book/Upstream Atlas Version 2 Website - Icons (from Matt)` 中提供的 26 个 SVG，替换 landing page 中对应的 26 个图标资源，同时保持仓库内现有资源路径不变。
- 将英文 topic reference 卡片的图标引用从 `.png` 切换为 `.svg`。
- 其余不在这 26 个映射内的 landing 图标位保持现状。
- 更新 landing-page 验证断言，确保生成页面使用这批提供的 hero 和 topic SVG。

## Capabilities

### New Capabilities
- `landing-page-icon-assets`: 当前 landing page 在可明确映射的 hero、stakeholder、search-scope、topic 图标位上，统一渲染用户提供的 26 个 SVG 图标资源。

### Modified Capabilities
- None.

## Impact

- 影响的源码生成：`scripts/shared/homepage-topic-reference.mjs`
- 影响的 landing 源 HTML：`editions/fr/site/index-main.html`
- 影响的资源目录：`assets/icons/homepage/`、`assets/icons/homepage-sprite.svg`、`assets/icons/search-scope/`、`assets/icons/stakeholders/`、`assets/icons/topics/`
- 影响的校验：`scripts/test-site-render.sh`
- 影响的生成结果：`public/index.html`、`public/fr/index.html` 以及复制后的 `public/assets/icons/*`
