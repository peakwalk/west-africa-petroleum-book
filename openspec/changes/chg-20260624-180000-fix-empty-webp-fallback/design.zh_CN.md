## Context

当前英文版 figure 资源里同时存在有效的 `figure-011.png` 和 0 字节的 `figure-011.webp`。章节 Markdown 仍然使用 canonical 的 `.webp` 引用，而 figure inventory 只按扩展名优先级选图，不看文件是否为空。因此 manifest 和章节页面都会优先使用坏资源。现有 coverage 校验只检查文件是否存在，也就把 0 字节资源误判为健康。

## Goals / Non-Goals

**Goals:**
- 在 WebP 有效时继续保持 canonical 的 `.webp` 命名契约。
- 在 figure inventory 选图时跳过空文件，并在同 stem 下回退到下一个有效格式。
- 当 Markdown 引用或 manifest 选中的 figure 资源为空文件时，让 coverage 校验直接失败。
- 仅修复当前英文版 Figure 11，不做大范围章节改写。

**Non-Goals:**
- 把所有章节图片引用统一改成 `.png`。
- 重构整条 figure 渲染链路。
- 引入超出“0 字节”范围的内容级图片损坏检测。

## Decisions

### Decision: 在 inventory 选图层过滤 0 字节文件
`_published_asset_candidates` 已经是发布素材优先级的单点入口。在这里拒绝空 WebP 并回退到有效 PNG，改动范围最小，而且不用改变 figure 编号或章节语义。

考虑过的替代方案：
- 在构建时动态重写章节 Markdown 图片引用。否决，因为改动面更大，而且 manifest 选图问题依然需要在 inventory 层修正。

### Decision: 把空引用素材视为校验失败
`check_docx_figures.py` 目前只验证“存在”，没有验证“可发布”。把 0 字节资源纳入失败条件，才能覆盖仍然引用 canonical `.webp` 的章节 Markdown，并让构建链路真正具备防回归能力。

考虑过的替代方案：
- 只保留 `_published_asset_candidates` 的单元测试。否决，因为这无法覆盖手工改过的章节引用，也无法发现磁盘上已存在的空资源。

### Decision: 只重生成 Figure 11 的 WebP
当前用户可见故障只落在 Figure 11。只重渲染这一张 bitmap WebP，能保持现有 canonical 引用名不变，也避免带来无关章节噪音。

## Risks / Trade-offs

- [未被引用的空素材仍可能留在磁盘上] → 新校验只覆盖 Markdown 引用和 manifest 已选中的资源；未发布的空文件可以暂时保留，这对本次 bugfix 可接受。
- [canonical 命名约束] → 现有测试和源章节普遍假定 `.webp` 名称存在；通过重生成 `figure-011.webp` 而不是重写引用，可以保持这个约束。
- [未来出现非零但损坏的文件] → 新规则只拦截空文件；如果未来出现非零但内容损坏的二进制，仍需要更强的完整性校验。

## Migration Plan

1. 先补失败测试，覆盖空 WebP 回退和英文版 Figure 11 产物非空。
2. 在 `scripts/docx_figures/inventory.py` 实现空文件过滤。
3. 扩展 `scripts/check_docx_figures.py`，报告空 Markdown 目标和空 manifest 目标。
4. 重生成 `editions/en/content/images/figure-011.webp`。
5. 重建英文版 figure manifest 和整站产物。
6. 如需回滚，恢复原有 inventory/checker 行为与旧 Figure 11 资源后，再重建 manifest。

## Open Questions

- None for this change.
