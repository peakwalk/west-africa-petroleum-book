## Why

首页 stakeholder 卡片目前指向的一套仓库内 SVG 已经和批准的截图参考不一致。问题不只是 CSS 摆位：其中几枚图标的轮廓、线条节奏和内部留白都变了，因此单靠 `offset` 无法做到像素级对齐。

用户现在已经提供了一套位于 `/Users/edison/Downloads/Project - Africa_Book/icons_pixel_replica_ultra_crisp_png_all/` 的 PNG 源 icon 包。我们需要一个范围很窄、完全仓库内自持的变更：把这 6 个 stakeholder PNG 正式引入项目，并把验证基线对齐到这套源文件上，再补上回归校验，避免后续首页调整再次把它们拉偏。

## What Changes

- 把用户提供的本地源 icon 包中的 6 个 homepage stakeholder PNG 引入首页，而不是继续对当前不匹配的图形做位置微调或手工重绘。
- 围绕这套引入源文件的光栅几何、透明留白和单色蓝色线稿风格建立 stakeholder 图标基线，使其在固定首页卡片内稳定渲染。
- 保持现有 stakeholder 卡片的 HTML 结构、固定 `120px` 宽度和桌面六列布局契约，只在需要把图标显示尺寸翻倍、统一视觉重量并让所有图标中心点落在同一条水平线上时做 CSS 调整。
- 为 stakeholder 图标补充聚焦的几何验证，保证未来修改后其 PNG 可见边界仍然稳定。

## Capabilities

### New Capabilities
- `homepage-stakeholder-icon-alignment`：首页 stakeholder 卡片渲染导入的源 PNG 集合，并在固定 `120px` 宽度的卡片网格内保持稳定几何、倍增后的显示尺寸，以及共用的图标中心线。

### Modified Capabilities
- None.

## Impact

- 影响的源生成文件：`scripts/shared/homepage-content.mjs`
- 影响的 landing 样式：`assets/css/landing.discovery.css`
- 影响的视觉资产：`assets/icons/stakeholders/*.png`
- 影响的验证：`scripts/test-site-render.sh` 与新增的定向图标几何测试
- 重建后受影响的生成输出：`index.html`、本地化首页输出，以及 `public/assets/icons/stakeholders/*`
