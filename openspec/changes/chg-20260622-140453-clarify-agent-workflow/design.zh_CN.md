## Context

当前 `AGENTS.md` 把 OpenSpec 和 Superpowers 压缩成了一小段要点。它足以表达“有这两个东西”，但还不足以稳定回答四个反复出现的问题：某次改动是否需要 OpenSpec、低风险文档或验证类编辑是否可以跳过、持久化的规划说明应该放在哪里，以及上游 Superpowers 的做法能否覆盖仓库本地的工作流约束。参考仓库 `oae-mono` 已经把这些歧义处理得更清楚。Africa Book 也需要同样的精度，但必须按它自己的书籍、站点、图表、本地化和验证工作流来改写，而不是直接照抄应用型 monorepo 的规则。

## Goals / Non-Goals

**Goals:**
- 给代理一条从第一性原理出发的决策路径：先判断改动类型，再判断是否需要 OpenSpec，再判断 Superpowers 是否有帮助，最后判断持久产物该落在哪里。
- 用 MECE 的方式组织规则，把它们拆成必须使用 OpenSpec 的情形、可以跳过的情形、文档规则、Superpowers 使用规则，以及冲突与完成标准。
- 保留仓库已经存在的优先级，例如中英文成对文档要求、图表工作流规则，以及“用最窄且有意义的验证”这条原则。

**Non-Goals:**
- 不改变书籍或站点行为，不修改构建脚本，也不调整图表流水线。
- 不要求每个任务都完整执行上游 Superpowers 工作流。
- 不追溯性地重命名或迁移历史 OpenSpec 变更目录。

## Decisions

### 1. 把“变更意图”与“执行技巧”分开

OpenSpec 负责持久化的变更意图：范围、需求、验证和回滚。Superpowers 只负责执行技巧：澄清、规划、测试纪律和复审。这样一来，当两者都相关时，就不会再对“谁说了算”产生歧义。

Alternative considered:
- 继续保留混合式的短列表，不明确责任边界。拒绝原因是这样会迫使代理每次都靠猜来推断政策边界。

### 2. 用贴合本仓库的 OpenSpec 分类

“必须使用”与“可以跳过”的规则，应该直接点名 Africa Book 的真实表面：书籍或站点行为、图表流水线、DOCX 对齐、落地页、构建与验证工作流、跨版本改动、生成产物，以及工作流政策。对这个仓库来说，这比一套泛化的软件架构术语更清楚。

Alternative considered:
- 逐字照搬 `oae-mono` 的规则清单。拒绝原因是其中很多分类面向应用或后端开发，在本仓库会引入噪音。

### 3. 活跃 OpenSpec 变更应成为同一改动唯一的持久事实来源

只要存在活跃变更，计划、复审说明、验收决定和 spec delta 都应与它放在一起。只有在 OpenSpec 不可用或不需要时，才允许把持久化的 Superpowers 产物放到回退目录 `docs/superpowers/**`。这样可以避免一个改动同时有两套互相漂移的规划记录。

Alternative considered:
- 允许同一项工作同时把持久计划写在 OpenSpec 和 `docs/superpowers/**` 两处。拒绝原因是迭代中极易出现“双脑”漂移。

### 4. 继续强制双语 OpenSpec 文档

这个仓库已经要求项目工作流文档有简体中文对应文件。OpenSpec 文档也应明确遵守同样的规则，避免工作流治理本身变成本仓库文档本地化政策的例外。

Alternative considered:
- 把 OpenSpec 的中文对应文件设为可选。拒绝原因是这会在仓库现有文档规则里埋下一个隐性的例外。

### 5. 上游 Superpowers 技能只在仓库规则之下作为辅助

本地 AGENTS 规则、仓库本地技能和用户明确指令，必须能够覆盖上游 Superpowers 中关于仅 TDD、创建 worktree 或清理分支之类的习惯。这能让仓库行为保持确定性，也能避免引入用户并未要求的流程成本。

Alternative considered:
- 只要存在上游技能就完整执行它。拒绝原因是这可能与仓库本地的验证、批准和文档规则冲突。

## Risks / Trade-offs

- [工作流文字变多，可能增加流程感] -> 通过明确的跳过清单降低额外成本，并允许低风险但非平凡的改动直接把 OpenSpec 变更当成工作计划使用。
- [回退目录 `docs/superpowers/**` 仍可能被滥用] -> 只在没有活跃 OpenSpec 变更，且 OpenSpec 不可用或不需要时允许使用，并在有 OpenSpec 时始终保持 OpenSpec 为权威来源。
- [双语 OpenSpec 维护会增加文档工作量] -> 接受这一成本，因为仓库本来就把中英文成对工作流文档当作长期契约。

## Migration Plan

- 在同一次变更里同步更新 `AGENTS.md` 与 `AGENTS.zh_CN.md`。
- 从现在开始，新建活跃 OpenSpec 变更默认使用 `chg-YYYYMMDD-HHMMSS-<slug>` 命名。
- 不追溯修改已归档或已接受的历史变更目录名。

## Open Questions

- None.
