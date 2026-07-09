## Context

当前 landing 实现已经按区域拆分了图标资源：hero stats 使用 `assets/icons/homepage/hero-*.svg`，stakeholder 卡片使用 `assets/icons/stakeholders/`，search-scope chip 使用 `assets/icons/search-scope/`，英文 topic-reference 卡片使用 `assets/icons/topics/`。用户提供的 26 个文件可以完整映射到这 4 组：6 个 hero、6 个 stakeholder、8 个 search-scope、6 个 topic。

这个变更刻意保持收敛，不重新调整 landing page 的信息架构、文案或整体布局系统。工作范围只包括：替换这 26 个可映射资源文件、保持 topic 卡片走 SVG 引用，并更新校验以匹配提供的文件。

## Goals / Non-Goals

**Goals:**
- 用用户提供的 26 个 SVG 替换可明确映射的 landing-page 图标位。
- 尽量保持现有资源路径不变，减少模板改动面。
- 将英文 topic-reference 卡片从 PNG 图标引用切换为 SVG。
- 保持英文与法语 landing 页面继续通过现有 site 构建链路生成。
- 扩展校验，确保英文首页不再依赖 PNG topic-card 图标路径。

**Non-Goals:**
- 不重做文案或 section 顺序。
- 不引入新的图标组件系统，也不把所有外部 SVG 改成内联。
- 不清理或重生成当前未参与渲染的历史 PNG 资源。
- 不替换这 26 个映射之外的其他 landing 图标位。

## Decisions

### Decision: 以用户提供的 26 个 SVG 文件作为图标事实源
所有替换资源都直接来自用户提供的图标包，并覆盖到仓库内对应的现有资源路径。这样可以最大程度遵循用户给定的美术风格，避免继续使用第三方图标库进行主观映射。

Alternative considered:
- 保留当前第三方图标替换结果。否决，因为用户已经明确要求改用提供的 26 个文件。

### Decision: 保留现有资源文件名和引用关系
本次改动会直接覆盖现有资源文件，而不是为每个图标引入新文件名。这样可以尽量减少模板层变更，并继续复用现有站点资源复制逻辑。

Alternative considered:
- 新建文件名并更新所有引用。否决，因为会增加改动噪音，但没有用户可见收益。

### Decision: 在 helper 层把 topic-reference 卡片从 PNG 切到 SVG
`scripts/shared/homepage-topic-reference.mjs` 会改为输出 `.svg` 图标路径，确保英文首页真正使用新的矢量资源。

Alternative considered:
- 保持页面继续引用 PNG，只更新旁边未使用的 SVG。否决，因为这样页面仍然会渲染旧的栅格图标。

### Decision: 严格只替换这 26 个可明确映射的 landing 资源
这套图标包并不覆盖法语兼容首页的 feature / audience / country-signal 图标位，也不覆盖自适应控制类 sprite 图标。因此这次改动只替换 26 个能明确映射的资源，其余图标位保持现状。

Alternative considered:
- 把这套图标强行扩展到更多入口。否决，因为文件名和数量只清晰对应 26 个图标位。

## Risks / Trade-offs

- [提供的自定义图标可能与上一步为第三方图标调过的尺寸不匹配] -> 将 stakeholder、search-scope、topic 这几组尺寸恢复到更适合这套图标的数值。
- [图标包只覆盖 landing page 的一部分入口] -> 严格限制在 26 个可映射入口内替换，其余保持不动。
- [topic 图标契约从 PNG 改成 SVG] -> 同步更新 `scripts/test-site-render.sh` 中的源码与生成页断言。
