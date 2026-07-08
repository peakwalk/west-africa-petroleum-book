## ADDED Requirements

### Requirement: Stakeholder icon rebuilds MUST use acceptance-driven multi-variant selection
项目 SHALL 基于批准后的截图参考图重建 stakeholder 图标包；对每个失败图标使用多个候选方案，再从中选出通过验收标准的最终版本并交付。

#### Scenario: Failing icons generate multiple reconstruction candidates
- **WHEN** 某个 stakeholder 图标未通过验收评审
- **THEN** 重建流程必须为该图标生成至少两套候选版本
- **THEN** 候选可以来自不同路线，例如截图描摹、代理矢量清理或手工 SVG 重建
- **THEN** 流程不能强制所有图标走同一种重建方法

#### Scenario: Final icon selection is based on comparison rather than first output
- **WHEN** 某个 stakeholder 图标存在多个候选版本
- **THEN** 工作流必须把这些候选与截图裁出的 source reference 做对比
- **THEN** 最终选中的版本必须是在定量比较和人工审查中表现最好的候选
- **THEN** 质量较差的候选不能静默进入最终交付

### Requirement: Final stakeholder icon package MUST pass acceptance as a complete set
项目 SHALL 只有在整套图标都通过交付包完整性、前端 SVG 语义、特殊图标规则和截图一致性审查后，才能把 stakeholder 图标重建包视为完成。

#### Scenario: Special-case icon rules remain enforced
- **WHEN** 重建 `oil_drop`
- **THEN** 最终 SVG 必须保留右侧负形切口，并且该区域为透明镂空
- **THEN** 最终图标不能退化成普通实心水滴

#### Scenario: Smooth vector delivery rejects rough trace output
- **WHEN** 对最终 SVG 做审查
- **THEN** 只要存在明显 tracing 毛刺、线条节奏断裂或肉眼可见的台阶边，就必须判定验收失败
- **THEN** 只有前端可正式使用的干净矢量几何才能通过

#### Scenario: Rebuild loop continues until all icons pass
- **WHEN** 任一图标仍未通过验收标准
- **THEN** 重建流程必须继续对该图标迭代
- **THEN** 在全部图标都通过之前，整套图标包都不能被认定为最终版本

### Requirement: Acceptance MUST distinguish baseline trace fidelity from production polish
项目 SHALL 维护两层验收：一层是用于候选筛选的 `baseline` trace fidelity gate，另一层是用于正式精修交付的更严格 `production` polish gate。

#### Scenario: Baseline acceptance remains useful for candidate filtering
- **WHEN** 以 `baseline` profile 检查重建图标包
- **THEN** 验收脚本必须验证截图相似度、交付包完整性、特殊负形规则以及基础前端 SVG 安全性
- **THEN** 通过 `baseline` 不能自动等同于“已经精修到最终交付水平”

#### Scenario: Production acceptance rejects stroke-like trace silhouettes
- **WHEN** 以 `production` profile 检查 `regulators`、`governments`、`shield_star`、`global` 这类线性主导图标
- **THEN** 最终交付必须使用 stroke-led 或同等手工可控的矢量几何，而不是 evenodd-filled 的 tracing 轮廓伪装线稿
- **THEN** 即使 baseline 的轮廓重合度仍然通过，只要仍有明显 trace 路径膨胀或线条抖动，就必须判定 production 失败

#### Scenario: Replacing homepage-facing icons requires production polish
- **WHEN** 某套 stakeholder 图标或 topic-card 图标被视为正式精修版前端替换资源
- **THEN** 该套图标除了通过 `baseline` 外，还必须通过 `production` profile
- **THEN** 在被认定为完全验收通过之前，仍然需要人工复核
