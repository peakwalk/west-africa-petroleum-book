## Context

仓库里现在已经有专门的 stakeholder 图标重建脚本、`artifacts/stakeholder_icons_trace_rebuild/` 下的对比预览包，以及一套基础自动验收。但这套基础验收也暴露了第二个问题：图标包可以通过截图一致性自动检查，却仍然达不到原设计稿的精致度。

这意味着本次变更现在有两个不同的质量目标：

- `baseline` trace fidelity：足够贴近截图，可用于候选筛选和真值对比。
- `production` polish：足够干净、足够克制、足够稳定，能作为正式精修图标交付，而不会让人一眼看出 tracing 的厚重感、抖动感或图库化倾向。

## Goals / Non-Goals

**Goals:**
- 产出一套最终通过验收的 stakeholder trace rebuild 图标包。
- 对每个失败图标生成多个候选版本，而不是强制所有图标走同一种重建方法。
- 始终把截图参考图作为轮廓和负形的最终真值。
- 保证最终 SVG 适合前端使用，PNG 导出在全部要求尺寸下稳定清晰。

**Non-Goals:**
- 重新打开与本任务无关的首页布局或 CSS 工作。
- 把单次自动描摹结果直接当成最终交付。
- 强行要求所有图标使用同一个重建方法。
- 在整套图标未通过验收前就结束本次变更。

## Decisions

### Decision: 对每个图标采用多候选方案生成
每个失败图标都至少生成两套候选。候选家族可以包括：基于截图的 trace、基于代理矢量的清理版本，以及纯手工 SVG 重建。最后交付的版本以“定量对比 + 人工审查”综合表现最佳者为准。

Alternative considered:
- 对 6 个图标都继续使用同一套全局流水线。Rejected，因为当前失败已经证明：有的图标更适合直接从截图重建，有的更适合从清理后的代理几何出发。

### Decision: 始终以截图轮廓为最终真值
即使某些图标会借助代理矢量做起稿，验收时仍然以截图裁出的 `source_reference` 为最终对照。代理矢量只能作为脚手架，不能成为真值来源。

Alternative considered:
- 对部分图标把仓库现有代理矢量提升为真值。Rejected，因为这会允许结果继续偏离用户提供的截图。

### Decision: 增加明确的 acceptance automation
重建流程里新增专门的 acceptance checker。它会验证：交付包完整性、SVG 语义、`oil_drop` 这类特殊负形约束，以及可量化的轮廓相似度基线，从而在人工审查之前先筛掉明显错误的候选。

Alternative considered:
- 只依赖预览图和人工肉眼判断。Rejected，因为用户要求的是可重复执行的“重建-验收-再重建”循环，而不是一次性主观判断。

### Decision: 把验收拆成 baseline 和 production 两个 profile
验收脚本和书面标准都会区分 `baseline` profile 与 `production` profile。`Baseline` 继续承担候选筛选和截图贴合度验证的职责；`Production` 则在此基础上增加更严格的 SVG 语义、路径经济性和最终人工精修 gate。

Alternative considered:
- 继续维持单一验收 profile，只把现有阈值调得更严。Rejected，因为重合度自动化和精修审查在本质上是在解决两个不同问题，不应该被压扁成一个数字。

### Decision: 自动描摹只允许作为草稿，不允许直接作为最终交付
自动描摹只用于生成 draft。只要最终结果仍然明显像直接位图描摹，无论轮廓覆盖率多高，都不能通过。

Alternative considered:
- 只要轮廓重合度足够高，就接受带 trace 粗糙边的版本。Rejected，因为验收标准要求的是正式可用的平滑矢量，而不仅仅是“看起来差不多”。

## Risks / Trade-offs

- [量化轮廓对比可能会奖励“重合度高但边缘粗糙”的 trace 结果] -> 让它只停留在 `baseline` 层，不再假装同一套分数就能衡量精修质量。
- [手工 SVG 重建容易滑向重新设计] -> 在所有 compare 预览中始终保留截图裁片，并拒绝被标准化成图库风格的候选。
- [每个图标不同方案会增加脚本复杂度] -> 让候选定义保持显式、按图标分开配置，而不是过度抽象成一套大而全流水线。
- [当前工作树已有其他无关改动] -> 只改 stakeholder 重建脚本、聚焦测试和本次变更自己的 OpenSpec 文档。

## Migration Plan

1. 更新 OpenSpec，记录新的多方案重建与反复验收策略。
2. 先为当前结果补上会失败的 acceptance automation。
3. 扩展重建脚本，让每个失败图标都能输出多个候选版本。
4. 生成对比预览和定量分数，为每个图标选出当前最优候选。
5. 对未通过的图标继续细化，并反复跑验收，直到整套通过。

## Open Questions

- None. 用户已经明确要求多方案生成、对比选优，并持续迭代到通过验收。
