# Africa Book 代理说明

## 仓库结构
- 书稿源文件位于 `editions/<locale>/content/` 下，英文版在 `editions/en/content/`，法文版在 `editions/fr/content/`。
- 落地页由 `scripts/generate-*.mjs` 生成；`public/` 是构建产物，不能直接编辑。
- 图表元数据位于各版本根目录下的 `editions/<locale>/content/images/figure-manifest.json`；修改图表资源或章节引用后，应重新生成对应版本的 manifest。
- 仓库专用工作流技能位于 `.agents/skills/mdbook-docx-figure-workflow/SKILL.md`。
- 仓库本地 Codex 插件脚手架位于 `plugins/africa-book-workflow/`，并注册在 `.agents/plugins/marketplace.json`。

## 文档本地化
- `AGENTS.zh_CN.md` 是本文件的简体中文对应版本。每次修改 `AGENTS.md` 时，都要保持两者同步。
- 后续新增任何非源码类项目开发 Markdown 文档时，都要在同目录添加对应的 `.zh_CN.md` 文件。例如：`docs/example.md` 应对应 `docs/example.zh_CN.md`。
- 该规则适用于代理/开发者工作流文档、计划、规格、政策，以及构建或发布说明。
- 该规则不适用于 `editions/<locale>/content/chapters/*.md` 中的书稿源文件、生成产物、第三方文档，或文件名已经包含语言区域后缀的 Markdown 文件。
- 修改已有的非源码项目文档时，如果它已经有 `.zh_CN.md` 对应文件，应在同一次变更中同步更新两份文件。

## 必需工具
- 核心工具链：`node`/`npm`、`python3`、`mdbook`。
- 基于 PDF 的图表渲染还需要带 macOS `PDFKit` 的 `swift`。
- `mdbook` 应能从 `PATH` 解析；在这台机器上，Homebrew 二进制路径是 `/opt/homebrew/bin/mdbook`。
- PDF 图表流水线的 WebP 输出是可选的。当没有可写 WebP 编码器时，`png` 是可接受的备用格式。

## OpenSpec 与 Superpowers 工作流

### 角色与边界
- 优先使用仓库本地技能。工作涉及章节、DOCX 对齐、图表、mdBook 输出或生成的站点资源时，`.agents/skills/mdbook-docx-figure-workflow/SKILL.md` 是必读参考。
- OpenSpec 是本仓库“要改什么”的持久权威系统，负责范围、非目标、验收标准、验证要求、回滚条件和长期需求。
- Superpowers 是“代理如何工作”的选择性执行辅助，负责澄清、方案探索、规划、测试纪律、增量执行和复审技巧。
- 不要为同一个变更维护并行的持久事实来源。只要 `openspec/changes/<change-name>/` 已存在，该目录就是权威记录。

### 何时必须使用 OpenSpec
- 对以下改动，应在大范围实现前创建或更新 OpenSpec 变更：新增用户可见的书籍或站点行为；图表渲染、图表元数据或 DOCX 对齐行为；落地页生成；构建、测试或验证工作流变化；插件或工作流政策变化；架构重构；跨多个章节、脚本、生成产物或版本的变更；以及任何验收标准、回滚条件或回归边界本来会含糊不清的改动。
- 只要是非平凡且由 AI 辅助完成的 bug 修复或重构，并且会改变行为而不只是整理代码结构，也必须有 OpenSpec。
- 对低风险但非平凡的工作，OpenSpec 变更本身可以直接作为工作计划，不必额外暂停等待批准；但如果用户、仓库安全规则或需求歧义要求确认，则仍然要先确认。
- 对高风险、跨版本、架构级、工作流/治理级或行为变更类工作，在 proposal、design、tasks 和 spec delta 完整且用户已批准方向之前，不要做大范围实现。

### 何时可以跳过 OpenSpec
- 以下情况通常可以跳过 OpenSpec：错别字修正、窄范围文案编辑、一次性章节对齐修正、对已触达文件做机械格式化、在已有规格变更后刷新生成产物，以及不改变预期行为的小型测试期望更新。
- 仅文档澄清类改动，只有在它不改变支持边界、架构、工作流规则、验证要求或操作行为时，才可以跳过 OpenSpec。
- 如果一项原本跳过 OpenSpec 的改动逐渐超出上述窄范围，应立即停止继续实现，先补建或更新 OpenSpec 变更。

### OpenSpec 文档规则
- 本地执行 OpenSpec 命令时，优先使用 `./node_modules/.bin/openspec ...`。
- 新建中的变更目录默认使用 `openspec/changes/chg-YYYYMMDD-HHMMSS-<slug>/` 命名。已接受的历史变更可以保留现有 ID。
- 每一份持久 OpenSpec 文档都必须在同一个变更目录里保持英文和简体中文对应文件同步：`proposal.md` + `proposal.zh_CN.md`、`design.md` + `design.zh_CN.md`、`tasks.md` + `tasks.zh_CN.md`，以及 `specs/<capability>/spec.md` + `specs/<capability>/spec.zh_CN.md`。
- 英文 OpenSpec 文件仍然是机器校验的权威文件；`.zh_CN.md` 文件是必须同步的人类可读对应版本。
- 一个 OpenSpec 变更至少应记录：问题本身、范围与非目标、受影响的文件、版本和能力、来源证据或上下文图谱、高风险面、实施任务、验收标准、验证或 desk check 计划，以及在需要时的回滚/降级条件和批准状态。

### Superpowers 使用规则
- 只有当 Superpowers 能实质性提升澄清、方案探索、设计复审、实施规划、特征化测试、小步可逆执行或最终复审时，才使用它。
- 不要假设完整的上游 Superpowers 工作流已经在本仓库启用。只有通过本地 Codex 技能发现路径明确暴露出来的技能，才算本仓库可用。
- 除非用户明确要求，或当前改动区域已经有可靠的仓库本地命令让该技巧值得使用，否则不要强制执行仅 TDD、git worktree 或分支清理流程。
- 如果 Superpowers 产出了持久化的设计说明、计划、任务拆分、验收标准或复审结论，应把这些内容写入当前 OpenSpec 变更，或写入另一个被本仓库认可的原生文档。
- 当某个变更已经有活跃的 OpenSpec 目录时，持久化的设计、计划、任务、验收、验证和复审决策都应落在 `openspec/changes/<change-name>/` 下。不要再为同一变更在 `docs/superpowers/**` 下单独创建持久文件，除非它们被明确标注为辅助证据，并回指权威 OpenSpec 路径。
- 如果当前没有活跃 OpenSpec 变更，且 OpenSpec 不可用或不需要，持久化的 Superpowers 产物可以放在 `docs/superpowers/specs/` 和 `docs/superpowers/plans/` 下；目录不存在时先创建，并使用可排序的时间戳前缀命名。

### 冲突处理与完成标准
- 如果 OpenSpec 与 Superpowers 冲突，OpenSpec 决定“做什么、为什么做、范围、非目标、验收标准、验证要求和回滚条件”；Superpowers 只决定“如何执行”。
- 用户指令、本仓库的 AGENTS 规则、仓库本地技能，以及必须遵守的验证和图表工作流规则，优先级都高于 OpenSpec 和 Superpowers。
- 如果冲突会影响范围、安全性、架构、验证方式或用户可见行为，应在编辑前先向用户确认。
- 不要只因为更新了 OpenSpec 或写完了 Superpowers 计划就声称完成；仍然必须完成实现，并运行与本次改动最相关、最窄范围的仓库验证。

## 常用命令
- `npm run build`
- `npm run build:site`
- `npm run test:site`
- `npm run check:docx-parity`
- `npm run check:docx-figures`
- `npm run render:pdf-figures -- --edition en --figures 17 23 24`
- `npm run render:pdf-figures -- --edition fr --figures 17 23 24`
- `npm run render:docx-chart-figures -- --edition en --figures 24 31 32`
- `npm run render:docx-chart-figures -- --edition fr --figures 24 31 32`
- `npm run render:docx-shape-figures -- --edition en --figures 23 25 26 27 28 29 30`
- `npm run render:docx-shape-figures -- --edition fr --figures 23 25 26 27 28 29 30`
- `npm run render:docx-vector-figures -- --edition en --figures 22`
- `npm run render:docx-vector-figures -- --edition fr --figures 22`

## 图表工作流
- 当 HTML 布局相对 PDF 漂移时，`shape_group`、`chart` 和 `composite` 图表优先使用 PDF 流水线。
- 当前已知的 PDF 支撑图表是 `17` 和 `23-32`。
- 只有当原生 DOCX 提取已经稳定，或明确要求时，才使用 DOCX 渲染器。
- 修改图表资源、图表引用或渲染脚本后：
  1. 重新渲染目标图表。
  2. 运行 `python3 scripts/build_docx_figure_manifest.py --edition <locale>`。
  3. 运行 `python3 scripts/check_docx_figures.py --edition <locale>`。
  4. 让 `scripts/test-site-render.sh` 的期望与发布资源路径和格式保持一致。

## 验证期望
- 章节文本编辑：针对被修改章节运行范围最窄且有用的 `check_docx_parity.py` 调用。
- 图表流水线编辑：运行相关的 `tests/docx_figures/*` 用例和 `check_docx_figures.py`。
- 主题/布局编辑：运行有针对性的 CSS/JS 测试；工具链可用时运行 `npm run test:site`。
- 有 OpenSpec 支撑的变更必须同时包含上面范围最窄的相关项目检查，以及仓库中可用的 OpenSpec 验证/检查。
- 当变更还影响图表生成、落地页脚本或站点断言时，不要只凭 `mdbook build` 就声称完成。
