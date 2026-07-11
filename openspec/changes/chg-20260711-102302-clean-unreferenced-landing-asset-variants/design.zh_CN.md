## Context

在前两轮 landing 清理之后，`assets/images/` 里仍然保留着几组历史 hero 试验图、一个退役的地图 inset 资源，以及更早的品牌/overlay 变体。全仓搜索表明，这些文件已经不再被生成后的 landing HTML、生成后的 landing CSS、landing 脚本或当前 reader shell 引用。

但 public 构建仍然会发布它们，因为 `scripts/build_site.mjs` 还是把整个 `assets/` 目录复制到两个 locale 的输出目录。这一批候选文件在源目录里大约有 `1.41MB`，落到两个 public 目录后大约会变成 `2.83MB` 的重复发布体积。

这次需要明确保留的边界，是 book-theme 的分页装饰资源链。`prototype-hero-graywhite-left.webp` 和 `prototype-hero-graywhite-right.webp` 仍然被 `theme/custom.css` 引用，对应保留的 PNG 备份也不在这次范围内。

## Goals / Non-Goals

**Goals:**
- 只删除没有运行时引用的历史资源变体。
- 保持当前 landing 资源和 book-theme 分页资源不变。
- 增加回归覆盖，确保这些删除的变体在源目录和构建产物目录里都保持缺失。

**Non-Goals:**
- 不修改 landing shell markup，也不修改 hero 样式契约。
- 这次不改 `build_site.mjs` 的按 locale 选择性复制策略。
- 不碰 `prototype-hero-graywhite-left.png`、`prototype-hero-graywhite-right.png`，也不碰仍在使用的 graywhite WebP 文件。

## Decisions

### Decision: 只删除无引用的历史变体
这次删除以下源文件：
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

Alternative considered:
- 顺手也删除 `prototype-hero-graywhite-left.png` 和 `prototype-hero-graywhite-right.png`。Rejected，因为这两个文件更接近仍在使用的 book-theme 资源链，而用户之前明确说过先不管 book theme。

### Decision: 把现有“存在但未使用”的断言改成“必须缺失”的断言
`scripts/test-site-render.sh` 现在还会对这批文件中的一部分做 size 或 existence 检查，尽管没有任何运行时表面在引用它们。这次会把契约翻转：源目录和两个 public 资源目录都必须保持它们缺失。

Alternative considered:
- 只删文件，不改测试。Rejected，因为 `build_site.mjs` 的整目录复制会让它们在后续很容易被静默带回来。

## Risks / Trade-offs

- [删除的文件可能仍有历史设计参考价值] -> 接受这个取舍，因为用户明确要求继续清理资源，而且这批文件没有任何当前运行时依赖。
- [这次没有解决复制策略本身的低效问题] -> 接受这个取舍，因为构建复制语义的调整属于单独的行为变更，适合拆成后续一轮。

## Migration Plan

1. 先加入针对这批无引用资源的失败型回归断言。
2. 从 `assets/images/` 删除这些历史资源变体。
3. 重建站点，让这些变体从两个 public 资源目录里一起消失。
4. 运行目标测试、站点校验和 OpenSpec 校验。
5. 如需回滚，恢复这些被删资源并回退缺失断言。

## Open Questions

- None for this change.
