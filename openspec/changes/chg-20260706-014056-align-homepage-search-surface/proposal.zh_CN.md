## Why

当前首页搜索区块与批准的参考图不一致。它把同一段标题同时渲染成 eyebrow 和主标题，并且仍然使用一个独立的提交按钮，而不是设计稿里那种一体化的宽搜索框。

首页相邻的 `Browse by Topic` 区域也仍然停留在更早的信息架构草稿上。它现在渲染成一个大段 editorial 标题加 10 张信息卡，而不是设计稿里那种紧凑的 6 张带图标 topic 卡片。

底部的 `section-summary-modules` 也仍然沿用旧的等宽卡片布局，并且缺少设计稿里那种可见 CTA 链接和绿色勾选列表样式。

用户已经给出了这三个区块的明确视觉目标。本次需要做一个范围可控的改动，把首页搜索标题和搜索框样式、英文首页 `Browse by Topic` 的卡片布局，以及英文首页底部 `summary-modules` 卡片行一起对齐到参考图，同时保留现有跳转目标、本地化文案和法文兼容首页行为。

## What Changes

- 更新首页搜索区块标记结构，改为单个可见的居中标题，以及带前置搜索控件/图标的一体化胶囊搜索框。
- 调整搜索区块的间距、宽度、边框、圆角、占位文本样式、响应式行为以及 search-scope chip 图标呈现，使桌面端和窄屏布局贴近批准参考图。
- 把英文首页 `Browse by Topic` 的大标题 + 10 卡片布局替换成设计稿里的 6 张 topic 参考卡片，并使用区块本地的内联 SVG 图标与更紧凑的文字层级。
- 调整英文首页底部 `summary-modules` 卡片行，使其贴近批准参考图，包括取消全大写风格的卡片标题、绿色勾选列表标记、更宽的 current-edition 卡片，以及底部可见的 action links。
- 保留现有搜索路由和搜索范围 chips，同时补齐与新标记和 CSS 对应的最小首页验证断言。
- 保留 topic 卡片现有章节跳转目标，同时让法文兼容首页继续保持当前 compact topic 布局。

## Capabilities

### New Capabilities
- `homepage-search-reference-alignment`：生成后的首页搜索区块以批准的“居中标题 + 一体化搜索框”构图呈现，同时不改变底层搜索目标页契约。
- `homepage-topic-reference-alignment`：生成后的英文首页 `Browse by Topic` 区块以批准的 6 张 topic 导航卡片呈现，同时不改变底层章节跳转目标。
- `homepage-summary-reference-alignment`：生成后的英文首页 `summary-modules` 区块以批准的 4 卡片收尾布局呈现，同时不改变底层跳转契约。

### Modified Capabilities
- None.

## Impact

- 受影响的生成源码：`scripts/shared/homepage-content.mjs`
- 受影响的生成辅助文件：`scripts/shared/homepage-topic-reference.mjs`
- 受影响的 landing 样式：`assets/css/landing.discovery.css`、`assets/css/landing.homepage-v2.css`、`assets/css/landing.modules.css`、`assets/css/landing.responsive-tablet.css`、`assets/css/landing.responsive-mobile.css`
- 重建后受影响的产物：`index.html`、`fr/index.html` 以及 `public/*` 首页变体
- 受影响的验证：`scripts/test-site-render.sh`
