## Context

首页当前已经对最重的视觉资源做过优化：hero 背景走 WebP，西非地图面板继续走 SVG，因为这个矢量资源比 raster 版本更小也更清晰。现在真正的首页异常点，是 current-edition 封面卡片还在引用 `assets/images/upstream-atlas-hero-book.png`。

这张 PNG 大约 `1.8MB`，分辨率是 `1024x1536`，但卡片样式里实际只按大约 `100px` 宽度显示。这个变更应该保持很窄：只优化这个首页封面表面，不动地图 SVG 合约，也不顺手重写其他 landing 图片策略。

## Goals / Non-Goals

**Goals:**
- 降低英文首页 current-edition 封面图的交付字节数。
- 把英文首页 current-edition 封面标记为非关键资源，避免它和 hero 争抢初始加载。
- 把改动限制在共享 homepage 生成器、一份仓库内资源和 landing 回归验证内。

**Non-Goals:**
- 不重做 summary module 布局，也不更换封面图内容。
- 不把首页地图面板从 SVG 改成 WebP。
- 不顺手改那些实测收益很小甚至更差的其他 landing PNG 资源。

## Decisions

### Decision: 增加一份首页专用的优化版 WebP 封面资源
首页会增加 `assets/images/upstream-atlas-hero-book.webp`，由现有 PNG 生成，并控制在适合 homepage 卡片的尺寸上。`640x960` 的 WebP 既能保留当前卡片所需清晰度，也能把体积明显压到原始 PNG 之下。

Alternative considered:
- 保留原 PNG，只增加 lazy loading。拒绝，因为这样没有解决主要的字节体积问题。

### Decision: 让共享 homepage 生成器直接引用优化后的 WebP
`scripts/shared/homepage-content.mjs` 会把 current-edition 卡片图片的 `src` 改成新的 WebP，并加上 `loading="lazy"` 和 `decoding="async"`。landing 首页本身已经在其他关键位置依赖 WebP，所以直接换 `src` 比为了这一个卡片引入 `picture` 标记和额外布局样式更窄。

Alternative considered:
- 使用带 PNG fallback 的 `picture`。拒绝，因为这会增加标记和 CSS 变动，但对当前已经依赖 WebP 的首页合约并没有实质收益。

### Decision: 同时用生成标记和构建产物大小做回归保护
单元级 homepage 生成测试会断言 WebP 路径和加载提示，`scripts/test-site-render.sh` 会断言构建产物不再输出 PNG 封面路径，并且新的 WebP 资源维持在明确的大小上限之内。

Alternative considered:
- 只做人工体积检查。拒绝，因为后续资源替换或重建时很容易再次引入回归。

## Risks / Trade-offs

- [仅用 WebP 的封面依赖现有 landing WebP 支持] -> 接受，因为 landing hero 目前本来就依赖 WebP 资源。
- [首页专用缩放资源不适合全屏复用] -> 保留原 PNG 作为可编辑的 source of truth，把新 WebP 严格限定在 homepage 卡片用途。
- [未来封面更新可能再次生成过大的文件] -> 增加构建产物大小断言，让 oversized 资源尽早失败。

## Migration Plan

1. 先加会失败的 homepage 回归检查，覆盖优化后的封面路径和加载提示。
2. 从现有 PNG 源生成 homepage WebP 封面资源。
3. 更新共享 homepage 生成器，让它引用 WebP 封面并带上 lazy/async 解码提示。
4. 重建站点，并运行聚焦 homepage 的验证和 OpenSpec 校验。
5. 如需回滚，把 homepage 封面切回 PNG 源，移除 WebP 引用后再重建站点。

## Open Questions

- None for this change.
