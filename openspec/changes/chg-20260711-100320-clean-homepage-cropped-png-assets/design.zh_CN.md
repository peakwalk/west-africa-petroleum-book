## Context

landing 首页的 feature card、audience card 和 country signal row 现在都只引用 `assets/icons/homepage-cropped/` 下的 WebP 文件。对应的 PNG 副本既没有被页面生成器引用，也没有被样式或当前运行时契约引用，现有校验里也只是断言 HTML 不会使用它们。

由于 `scripts/build_site.mjs` 会把整个 `assets/` 目录复制到两个 locale 的输出目录，这 10 个未使用 PNG 仍会被带进 `public/assets/icons/homepage-cropped/` 和 `public/fr/assets/icons/homepage-cropped/`。它们在源目录里合计大约 `115KB`，在两个 public 目录里又会再带来大约 `230KB`。

目录里的 README 也已经过时。它仍然把 PNG 描述为 first-class production assets，但当前 landing 契约实际使用的是 WebP。

## Goals / Non-Goals

**Goals:**
- 从源目录和构建产物里删除未使用的 cropped icon PNG 变体。
- 保持 WebP 资源不变，继续作为当前 landing 契约。
- 让本地 README 与实际使用的资源格式保持一致。

**Non-Goals:**
- 不重绘也不重新导出 cropped icon 图稿。
- 不把现有 WebP 图标集替换成 SVG 或其他格式。
- 不修改这些图标对应的 homepage markup 或 CSS selector。

## Decisions

### Decision: 只退役未使用的 PNG icon 副本
这次只删除 `assets/icons/homepage-cropped/` 下的 10 个 `.png` 文件，保留 `.webp` 文件不变。

Alternative considered:
- 把 PNG 当成归档设计源文件继续保留。Rejected，因为它们不属于当前运行时契约，会被重复复制进两个 public 目录，也没有任何当前自动化生成步骤依赖它们。

### Decision: 更新目录说明，避免继续保留过时格式描述
`assets/icons/homepage-cropped/README.md` 会改为描述 WebP 才是当前生产资源，并继续说明 control icon 仍应留在 SVG sprite 中。同时新增对应中文文件，满足仓库文档本地化规则。

Alternative considered:
- 完全不改 README。Rejected，因为删掉 PNG 后，README 会立刻与目录状态矛盾。

### Decision: 同时约束源目录和构建产物的缺失状态
增加测试覆盖，要求这些 PNG 变体在 `assets/icons/homepage-cropped/`、`public/assets/icons/homepage-cropped/` 和 `public/fr/assets/icons/homepage-cropped/` 中都保持缺失。

Alternative considered:
- 只依赖 HTML 不引用 PNG 的断言。Rejected，因为构建会复制整个资源树，未使用文件仍可能被静默发布。

## Risks / Trade-offs

- [这些 PNG 将来可能对人工重新导出还有用] -> 接受这个取舍，因为仓库已经保留了当前有效的 WebP 输出，而这些被删文件没有任何当前自动化依赖。
- [README 现在会变得更依赖具体格式] -> 接受这个取舍，因为准确文档比继续保留过时格式说明更重要。

## Migration Plan

1. 先为 cropped icon PNG 缺失契约加入失败型回归校验。
2. 更新 cropped icon 的 README 文件，使其描述 WebP 契约。
3. 从源目录删除这些 PNG 图标副本。
4. 重建站点，让两个 public 资源目录里的 PNG 一并消失。
5. 运行目标测试、站点校验和 OpenSpec 校验。

## Open Questions

- None for this change.
