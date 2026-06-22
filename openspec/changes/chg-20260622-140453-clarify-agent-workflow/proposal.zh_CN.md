## Why

当前 `AGENTS.md` 已经要求代理同时使用 OpenSpec 和 Superpowers，但它还没有把两者在低风险与高风险工作中的边界划分得足够精确。这会带来两类可避免的问题：一类是当工作流或行为契约已经发生变化时，代理仍然跳过 OpenSpec；另一类是代理过度套用 Superpowers，产出与仓库权威记录相互漂移的并行持久文档。

## What Changes

- 将仓库中的 OpenSpec 与 Superpowers 指南改写为 MECE 的几个部分，分别覆盖角色边界、必须使用 OpenSpec 的情形、可以跳过的情形、文档规则、Superpowers 使用规则和冲突处理。
- 增加仓库本地规则，明确 OpenSpec 变更命名、英文与中文对应文件，以及当 OpenSpec 不可用或不需要时，Superpowers 持久产物的回退存放位置。
- 在更新 `AGENTS.md` 的同时更新 `AGENTS.zh_CN.md`，让仓库继续保持一套中英双语一致的工作流契约。

## Capabilities

### New Capabilities
- `agent-workflow-governance`：定义 Africa Book 代理如何判断何时必须使用 OpenSpec、Superpowers 如何辅助执行、持久工作流产物应该落在哪里，以及两者冲突时如何处理。

### Modified Capabilities
- None.

## Impact

- 受影响文档：`AGENTS.md`、`AGENTS.zh_CN.md`
- 新增 OpenSpec 变更文档目录：`openspec/changes/chg-20260622-140453-clarify-agent-workflow/`
- 政策中引用的回退文档目录：`docs/superpowers/specs/`、`docs/superpowers/plans/`
- 不直接修改书稿内容、构建产物或图表资源
