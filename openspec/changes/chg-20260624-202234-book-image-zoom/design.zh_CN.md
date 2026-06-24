## Context

当前 reader 已经在 `theme/custom.js` 里把章节内容重写成 `.figure-card` 结构。因此增强逻辑仍然需要在 figure 卡片生成之后挂载，但如果把查看行为交给浏览器在新标签页里展示原图，就不再需要自定义 overlay、手势系统或内部滚动锁定。

同时，当前 figure 资源混合了 raster 和 vector 格式（`webp`、`png`、`svg`），所以方案仍然应该以用户点击的图片 URL 作为唯一事实来源，不去触碰素材管线。

## Goals / Non-Goals

**Goals:**
- 让用户比当前 inline 阅读宽度更容易查看正文 figure 图片。
- 把交互范围限制在已生成的正文 figure 卡片内。
- 同时支持点击和键盘激活。
- 复用浏览器原生的图片查看行为，而不是继续维护自定义缩放 surface。
- 不修改章节 Markdown、figure manifest 或图片资源管线。
- 移除 vendored pan/zoom 依赖，简化运行时代码。

**Non-Goals:**
- 不再构建页内 overlay、gallery、carousel 或 figure 前后切换。
- 不尝试统一不同浏览器的原生图片查看 UI。
- 不为封面图、落地页图片、侧栏图标或其他非正文图片开启这种行为。
- 不把 figure 资源重生成或重命名作为该功能的一部分。

## Decisions

### Decision: 只把生成后的 reader figure 卡片图片视为可打开目标
增强逻辑继续只针对 `.reader-article .figure-card img`，并在安装阶段把这些图片标记为可聚焦、可打开。这样可以和现有的 reader figure chrome 保持一致，也能避免误伤书壳层或站点营销区的图片。

考虑过的替代方案：
- 直接绑定所有 `.content img`。否决，因为这会影响需求范围外的非 reader 图片和装饰图。

### Decision: 在新标签页中打开原图资源
运行时通过用户直接触发的事件在新的浏览器标签页中打开被点击的图片 URL，并把全尺寸图片查看、缩放与平移行为交给浏览器处理。这样就不再需要在主题里维护自定义 overlay 生命周期、fit 算法、手势系统和关闭状态模型。

考虑过的替代方案：
- 继续迭代页内 overlay viewer。否决，因为 fit 和手势链路已经表现出比“浏览器原生回退方案”更高的维护成本。

### Decision: 移除本地 pan/zoom 依赖
既然浏览器直接负责展示原图标签页，主题就不再需要 vendored pan/zoom helper，也不再需要 `book.toml` 里的额外脚本加载顺序。

考虑过的替代方案：
- 保留 vendored helper，以备未来再启用 custom viewer。否决，因为未使用的运行时依赖和断言只会增加维护面。

## Risks / Trade-offs

- [图片查看不再发生在章节页内部] -> 接受这个取舍，以换取更简单、更可靠的行为；原章节标签页仍然保留。
- [浏览器原生图片查看体验在不同浏览器间会有差异] -> 接受这一点，因为这条路径本来就是刻意把缩放/平移 UX 委托给浏览器，而不是自己重写。
- [新标签页行为依赖用户直接触发事件] -> 只在直接点击或键盘激活时触发新标签页打开。
- [未来内容可能把 figure 图片包进链接] -> 安装交互时只处理生成后的 figure-card 图片，并跳过已经处于锚点内部的图片。

## Migration Plan

1. 更新 OpenSpec proposal、design、tasks 和 capability spec，使其描述“新标签页打开原图”的浏览器原生方案。
2. 移除 vendored pan/zoom 依赖及其相关源码级断言。
3. 用轻量的新标签页打开处理器替换 `theme/custom.js` 里的 custom viewer 实现。
4. 删除过期的 viewer CSS，同时保留键盘激活所需的 focus affordance。
5. 先跑最小必要的 theme 与站点校验，再做更大范围站点验证。

## Open Questions

- None for this change.
