## Context

landing shell 当前把 `assets/images/upstream-atlas-favicon.png?v=2` 同时写进了浏览器 favicon、shortcut icon 和 Apple touch icon 三个关系里。这个源文件是 `240x256`，大小大约 `45KB`。对 tab icon 来说这明显偏大，而 Apple touch icon 仍然更适合单独使用较大的正方形 PNG。

这个变更应该保持很窄。它只需要改善 landing shell 的图标交付方式，保留 PNG 兼容性，不碰 homepage 视觉或 book reader 行为。

## Goals / Non-Goals

**Goals:**
- 降低 landing 路由在普通浏览访问时加载的 favicon 字节数。
- 明确把 Apple touch icon 从小尺寸 tab icon 里拆出来。
- 把改动限制在 landing shell 标记、favicon 资源和 landing 验证范围内。

**Non-Goals:**
- 不把 favicon 切到 WebP。
- 不重做图标设计。
- 这一步不顺手修改 `theme/index.hbs` 里的 mdBook reader favicon 交付。

## Decisions

### Decision: 基于现有源图新增两个 landing 专用 PNG 派生产物
仓库继续保留 `assets/images/upstream-atlas-favicon.png` 作为可编辑源文件，同时新增：
- `assets/images/upstream-atlas-favicon-32.png`，用于浏览器 tab favicon 和 shortcut icon
- `assets/images/upstream-atlas-apple-touch-icon.png`，用于 Apple touch icon

这两个新资源都由现有源图生成，先补成正方形画布，再去掉无用元数据。

Alternative considered:
- 继续保留单个 PNG，只做重压缩。拒绝，因为浏览器 tab 路径依然不需要 `240x256` 的载荷。

### Decision: 只更新共享 landing 头部生成器
`scripts/shared/landing-shell.mjs` 会把 `rel="icon"` 和 `rel="shortcut icon"` 切到更小的 favicon，而 `rel="apple-touch-icon"` 改成单独的大 PNG。这样 landing、legal 和 chapters shell 页面都能一次受益，同时不把范围扩到 book reader theme。

Alternative considered:
- 同一步同时改 landing shell 和 book theme。当前拒绝，为了保持和用户要求的 landing page 范围一致。

### Decision: 用路径断言和体积阈值锁住新合约
回归测试会断言生成的 landing 输出包含新的 favicon 与 touch icon 路径，built-site 检查会给这两个新 PNG 派生产物加上明确的大小上限。

Alternative considered:
- 只检查资源存在。拒绝，因为这样回退到旧的 oversized favicon 路径也依然能通过。

## Risks / Trade-offs

- [两个资源替代一个源路径] -> 保留原始源文件，并从它派生两个新文件，降低后续更新复杂度。
- [landing 与 book 页面的 favicon 交付暂时不一致] -> 接受，因为这次用户问的是 landing 页面；后续可以单独再对齐 mdBook theme。
- [Apple touch icon 被请求时仍有一定字节成本] -> 接受，因为它不属于普通页面加载路径，而且仍然比过去一张通用大图更合理。

## Migration Plan

1. 先加会失败的 landing shell 分离 favicon 合约测试。
2. 从现有源 PNG 生成新的 `32x32` favicon 和 `180x180` Apple touch icon。
3. 更新 `scripts/shared/landing-shell.mjs`，让它引用分离后的资源。
4. 重建站点，运行聚焦 landing 的验证，并校验 OpenSpec change。
5. 如需回滚，把 landing shell 切回原先的单一路径，并删除派生资源。

## Open Questions

- None for this change.
