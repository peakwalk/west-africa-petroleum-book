## ADDED Requirements

### Requirement: 代理在大范围实现前必须先判断是否需要 OpenSpec
在开始大范围实现之前，代理必须根据仓库实际表面判断该改动是否需要 OpenSpec。对于 Africa Book，凡是涉及用户可见的书籍或站点行为、图表渲染或图表元数据行为、DOCX 对齐行为、落地页生成、构建或验证工作流变化、工作流政策变化、跨版本或跨多个章节/脚本的改动、架构重构，或任何验收、回滚与回归边界本来会不清晰的改动，都必须先创建或更新 OpenSpec 变更。

#### Scenario: 工作流政策变更必须先有 OpenSpec 变更
- **WHEN** 代理要更新 `AGENTS.md` 这类仓库工作流政策
- **THEN** 代理会在大范围落实该政策变更之前先创建或更新对应的 OpenSpec 变更

#### Scenario: 窄范围文案编辑可以跳过 OpenSpec
- **WHEN** 代理只是在修正错别字或进行不改变工作流规则、验证要求与操作行为的窄范围文案编辑
- **THEN** 代理可以跳过 OpenSpec

#### Scenario: 原本跳过的改动扩大了范围
- **WHEN** 一项原本跳过 OpenSpec 的改动扩大成了行为、工作流或验证政策变更
- **THEN** 代理会先停止继续实现，转而创建或更新 OpenSpec 变更，再继续后续工作

### Requirement: 活跃的 OpenSpec 变更必须是权威的持久事实来源
只要某项工作已经存在 `openspec/changes/<change-name>/`，持久化的设计、任务、验收、验证和复审决策都必须放在那里。代理还必须在同一个变更里保持 proposal、design、tasks 和 spec 文档的英文与简体中文对应文件同步。

#### Scenario: 持久规划说明保留在活跃变更目录内
- **WHEN** 某项工作已经存在 `openspec/changes/<change-name>/`，且代理又产出了持久化的规划或复审说明
- **THEN** 代理会把这些持久说明放进该变更目录，而不是在别处再创建一套并行的持久事实来源

#### Scenario: 英文 OpenSpec 文档更新时同步中文对应文件
- **WHEN** 代理创建或更新 `proposal.md`、`design.md`、`tasks.md` 或 `specs/<capability>/spec.md`
- **THEN** 代理也会在同一个变更里同步创建或更新对应的 `.zh_CN.md` 文件

### Requirement: Superpowers 必须选择性使用，并服从仓库规则
只有当 Superpowers 能显著提升澄清、规划、测试纪律、增量执行或复审效果时，代理才应使用它。代理不得假设完整的上游 Superpowers 工作流已经在本仓库启用；用户指令、仓库本地技能和仓库工作流规则，必须优先于上游 Superpowers 中关于仅 TDD、git worktree 或分支清理等习惯。

#### Scenario: 上游的仅 TDD 建议不能覆盖仓库本地规则
- **WHEN** 某个上游 Superpowers 技能建议对本仓库当前任务强制执行仅 TDD 流程
- **THEN** 代理会优先遵守仓库本地工作流规则和用户指令，而不会机械地强制执行仅 TDD

#### Scenario: 仓库本地图表工作流仍然优先
- **WHEN** 工作涉及章节、DOCX 对齐、图表、mdBook 输出或生成的站点资源
- **THEN** 代理仍然会把 `.agents/skills/mdbook-docx-figure-workflow/SKILL.md` 作为必须遵守的仓库本地工作流参考

### Requirement: Superpowers 的持久产物必须使用批准的位置
当 OpenSpec 不可用或不需要时，持久化的 Superpowers 产物必须放在 `docs/superpowers/specs/` 或 `docs/superpowers/plans/` 下，并使用可排序的时间戳前缀命名。只要某项工作已经有活跃 OpenSpec 变更，代理就不得再为同一变更在变更目录之外创建并行的持久文档，除非该文档被明确标注为辅助证据，并回指权威 OpenSpec 路径。

#### Scenario: 没有活跃 OpenSpec 变更时使用回退目录
- **WHEN** 代理需要保存一份持久化的 Superpowers 设计或计划，而当前没有活跃 OpenSpec 变更，因为 OpenSpec 不可用或不需要
- **THEN** 代理会把该文档放在 `docs/superpowers/specs/` 或 `docs/superpowers/plans/` 下，并使用可排序的时间戳前缀

#### Scenario: 已有活跃 OpenSpec 变更时禁止并行持久计划文档
- **WHEN** 当前工作已经存在活跃 OpenSpec 变更
- **THEN** 代理不会再为同一变更在 `docs/superpowers/**` 下创建第二份持久设计或计划文档；如果确有必要，也必须明确标注为辅助证据，并回指权威变更路径

### Requirement: 声称完成前必须有实现与仓库相关验证
代理不得只因为更新了 OpenSpec 或写完了 Superpowers 计划就声称工作完成。对于有 OpenSpec 支撑的改动，完成声明必须同时包含已落实的编辑、与本次改动最相关且范围最窄的仓库验证，以及仓库中可用的 OpenSpec 校验。

#### Scenario: 只更新 OpenSpec 还不能声称完成
- **WHEN** 代理只更新了 OpenSpec 文档，但尚未落实请求的改动，或尚未运行相关验证
- **THEN** 代理不会声称该工作已经完成
