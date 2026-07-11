## Context

landing 页面当前真正使用的图片集合，已经比 `assets/images/` 里保留的文件小得多。当前有效契约主要是：
- `assets/images/upstream-atlas-nav-logo.webp`，用于 landing header/footer 的品牌 lockup
- `assets/images/upstream-atlas-icon.png`，用于紧凑图标
- `assets/images/upstream-atlas-hero-book.webp`，用于英文首页 current-edition 卡片
- `assets/images/homepage-west-africa-map-panel.svg`，用于首页地图面板
- `assets/images/upstream-atlas-favicon.png` 作为可编辑 favicon 源文件，再派生出 split landing favicon 资源

与此同时，`scripts/build_site.mjs` 会把整个 `assets/` 目录复制到两个 locale 的输出目录。这意味着一批已经退役的图片，即使生成的 HTML 完全不再引用，也仍会继续出现在 `public/assets/images/` 和 `public/fr/assets/images/` 中。保守盘点后，这次可安全清理的源资源本身大约有 `2.9MB`。

## Goals / Non-Goals

**Goals:**
- 只删除没有当前运行时引用的 landing 历史图片。
- 保留仍然给当前优化交付链路提供源文件的 active source-of-truth 图片。
- 增加回归校验，确保这些退役文件在源目录和构建产物中都继续缺失。

**Non-Goals:**
- 不改 book reader theme 资源，也不改 chapters 页面图片契约。
- 不删除仍在使用的可编辑源文件，比如 `upstream-atlas-hero-book.png` 或 `upstream-atlas-favicon.png`。
- 这次不处理 `assets/icons/homepage-cropped/*.png` 这组源图。

## Decisions

### Decision: 把清理范围限制在保守确认过的退役文件清单
这次只删除 `assets/images/` 下那些在 landing 生成脚本、landing 样式和 landing 校验契约里都没有当前引用的图片。

退役文件清单：
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

Alternative considered:
- 一次性删除所有未被引用的 landing PNG 和旧 hero 版本。Rejected，因为其中有些文件仍被当作可编辑源资料记录，或者需要单独复核，避免额外 churn。

### Decision: 同时校验源目录和构建产物都不再包含这些文件
`tests/test_public_editions.py` 负责约束源目录，保证这些退役文件保持删除状态；`scripts/test-site-render.sh` 负责约束构建产物，保证资源复制过程不会把它们重新带回 `public/assets/images/` 和 `public/fr/assets/images/`。

Alternative considered:
- 只删文件，依赖后续 `git diff` 人工审查。Rejected，因为 `scripts/build_site.mjs` 是整目录复制，回归很容易被忽略。

## Risks / Trade-offs

- [某些文件可能仍有非正式设计历史价值] -> 接受这个取舍，因为这批文件没有当前运行时引用，而且用户明确要求清理 landing 历史图片资产。
- [这次清理是刻意不求全的] -> 接受这个取舍，因为保守范围可以避免误删当前源链路或更广的 theme 资源。

## Migration Plan

1. 先为退役文件清单添加失败型回归校验，覆盖源目录和构建产物。
2. 从 `assets/images/` 删除这些退役源文件。
3. 重建站点，确保 `public/assets/images/` 和 `public/fr/assets/images/` 不再包含这些文件。
4. 运行最小充分的 landing 测试、site render 校验和 OpenSpec 校验。
5. 如需回滚，恢复被删除的资源文件，并移除这些缺失断言。

## Open Questions

- None for this change.
