## Why

当前这套 stakeholder 图标重建包已经可以通过较粗粒度的截图一致性检查，但仍然达不到设计稿所要求的精致度。当前剩下的问题，已经不是“像不像截图”，而是“是否已经精修到可以作为正式前端图标交付”。

因此，验收模型本身需要更新。继续用单一的通过/失败标准已经不够，因为当前图标包可以通过重合度驱动的基础检查，但肉眼仍然会觉得过于 tracing、过重或过于图库化。项目需要一层标准用于候选筛选，另一层标准用于最终精修交付。

## What Changes

- 把验收拆成 `baseline` trace fidelity 验收和 `production` polish 验收两层。
- 让 `baseline` 验收继续聚焦截图贴合度、负形保留、前端安全性和交付包完整性，以便候选筛选仍然可自动化。
- 新增更严格的 `production` polish gate，覆盖光学精修、stroke 语义、路径经济性，以及最终交付前必须经过的人工审查。
- 更新自动验收脚本和测试，使当前图标包继续能通过 `baseline`，但在手工精修完成前明确无法通过 `production`。
- 在 proposal、design、spec、tasks、验收标准和验收评审中同步记录新的分层验收模型。

## Capabilities

### New Capabilities
- `homepage-stakeholder-icon-alignment`：项目能够生成并审阅一套 trace 重建的 stakeholder 图标包；最终 SVG/PNG 资产从多个候选方案中择优选出，并通过批准后的验收标准。

### Modified Capabilities
- None.

## Impact

- 受影响的重建工具：`scripts/build_stakeholder_icons_trace_rebuild.py`
- 受影响的验证：新增专用 acceptance checker 及其聚焦测试
- 受影响的评审产物：`artifacts/stakeholder_icons_trace_rebuild/` 下的预览图、对比图、metadata 和 review notes
- 受影响的 OpenSpec 产物：本变更下的 proposal、design、spec、tasks、验收标准和验收评审文档
