## ADDED Requirements

### Requirement: Homepage stakeholder cards MUST render the imported stakeholder source set with stable raster geometry
首页 SHALL 使用一组从用户提供的 stakeholder 源 icon 包导入、并由仓库自持的 PNG 来渲染 6 张 stakeholder 卡片；这些图标必须保留该源文件集合的轮廓、单色线稿风格和渲染后可见边界，以至于整排卡片不再依赖大幅 CSS 补偿才能看起来对齐。

#### Scenario: Imported source silhouettes replace the mismatched icon set
- **WHEN** 首页在桌面端渲染 stakeholder 卡片
- **THEN** 每张卡片都使用对应 stakeholder 类型的导入仓库自持 PNG 资产，而不是当前不匹配的造型
- **THEN** 图标处理保持单色蓝色线稿，不包含强调色圆点或双色细节

#### Scenario: Fixed-width card boxes preserve stable icon alignment at doubled display size
- **WHEN** stakeholder PNG 资产在固定 `120px` 宽度的卡片布局内渲染
- **THEN** 它们的可见边界必须足够稳定，以至于每张卡片只需要很小的光学尺寸微调
- **THEN** 图标显示尺寸相对于此前导入资产后的 CSS 基线翻倍，而不是继续停留在较小的占位比例
- **THEN** 6 个渲染后图标的中心点都落在同一条水平线上
- **THEN** 图标对齐不能依赖 PNG 画布内隐藏的大量留白差异

#### Scenario: Geometry regression catches visible-bound drift
- **WHEN** 仓库中的 stakeholder PNG 资产发生变化
- **THEN** 聚焦验证会在其固定像素尺寸上检查并裁切每个资产
- **THEN** 只要某个图标的可见边界框偏离导入源文件基线，验证就必须失败
