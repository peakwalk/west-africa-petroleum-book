## Context

在前几轮资源清理之后，仓库里的源资源已经小了很多，但 `scripts/build_site.mjs` 仍然会通过整棵复制 `assets/` 的方式，把超出运行时所需的文件重新发布到两个 locale 输出目录。

这种整树复制目前带来两类浪费：
- 一类是 source-only 文件仍会进入 public 输出，比如 `upstream-atlas-hero-book.png` 和保留下来的 graywhite PNG 备份；
- 另一类是只属于英文首页的资源仍会进入 `public/fr/assets/`，比如首页封面 WebP、首页地图面板 SVG，以及 cropped WebP 图标集。
- 此外，英文根输出里还保留着一批生成页面已经不再直接引用的 icon 目录，包括 `country-flags.svg`、发布到 public 的 `stakeholders/` 与 `topics/` 目录，以及整个 `homepage/` 图标目录。

这次改动需要保持很窄。它只改最终的资源复制阶段，保持当前生成后的 markup 和 CSS 契约不变，同时保留活跃的 book-theme 图片链路。

## Goals / Non-Goals

**Goals:**
- 停止把 source-only 图片复制进 public 输出。
- 停止把只属于英文首页的资源复制到 `public/fr/assets/`。
- 保持英文 landing、法文 landing，以及两个 book 输出当前所有运行时资源引用继续有效。

**Non-Goals:**
- 不重设计 landing 或 book 页面。
- 不修改生成后的 HTML/CSS 资源引用。
- 这次不追求把两个 public 资源树都压到理论最小。

## Decisions

### Decision: 使用显式 shared / English-only 资源清单
`scripts/build_site.mjs` 会定义：
- 一份 shared 资源清单，同时复制到 `public/assets/` 和 `public/fr/assets/`
- 一份 English-only 资源清单，只复制到 `public/assets/`

shared 清单保留以下运行时所需资源：
- 两个 landing shell
- 两个 legal / chapter landing 页面
- 两个 book 输出

English-only 清单只保留英文首页需要的资源，例如：
- `assets/images/homepage-west-africa-map-panel.svg`
- `assets/images/upstream-atlas-hero-book.webp`
- `assets/icons/homepage-cropped/*.webp`

Alternative considered:
- 解析生成后的 markup 和 CSS，自动推导完整资源清单。Rejected，因为这会引入更多机制和更高回归风险，而当前这一步只需要一个小而显式的清单。

### Decision: 停止发布 source-only 图片备份
只用于编辑或再生成的源图，比如 `upstream-atlas-hero-book.png` 和 `prototype-hero-graywhite-left.png`，继续保留在仓库里，但不再复制到 public 输出。

Alternative considered:
- 直接把这些源文件从仓库删除。Rejected，因为它们仍然作为可编辑源资料被保留，而这次变更只处理发布范围。

### Decision: 去掉英文根输出里不再被任何生成页面引用的 icon 目录
英文根输出将停止发布：
- `assets/icons/country-flags.svg`
- `assets/icons/homepage/*`
- `assets/icons/stakeholders/*`
- `assets/icons/topics/*`

法文输出则只保留它的 landing 页面当前仍直接引用的 6 个 homepage SVG 图标，其余 `assets/icons/homepage/` 文件都不再发布。

Alternative considered:
- 因为旧断言还要求这些 icon 目录存在，所以继续保留它们。Rejected，因为这些断言反映的是历史复制行为，不是当前运行时需求。

## Risks / Trade-offs

- [显式资源清单未来可能与新的运行时引用漂移] -> 接受这个取舍，并通过 site-render 断言约束缺失契约。
- [French homepage SVG 清单现在需要显式维护更小的子集] -> 接受这个取舍，因为运行时引用是明确且有限的。

## Migration Plan

1. 先加入针对 source-only public 图片和法文树英文首页资源的失败型断言。
2. 在 `scripts/build_site.mjs` 中实现 shared / English-only 选择性复制。
3. 重建站点，验证两个 locale 输出树仍满足现有页面契约。
4. 校验 OpenSpec 变更文档。

## Open Questions

- None for this change.
