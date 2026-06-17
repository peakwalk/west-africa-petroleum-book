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
- 在开始非平凡工作时使用 Superpowers。请求含糊时使用其澄清或头脑风暴工作流；在编辑代码、渲染脚本、测试或书籍生成逻辑前，使用其规划和 TDD 导向工作流。
- 优先使用仓库本地技能。工作涉及章节、DOCX 对齐、图表、mdBook 输出或生成的站点资源时，`.agents/skills/mdbook-docx-figure-workflow/SKILL.md` 是必读参考。
- 使用 OpenSpec 作为持久产品、工作流、构建、图表流水线和站点生成规格的权威来源。
- 新增用户可见的书籍/站点行为、图表渲染或图表元数据行为、DOCX 对齐规则、落地页生成、插件行为、构建/测试工作流、影响多个章节/脚本/生成输出的变更、架构重构和工作流政策变更，都必须有 OpenSpec 变更。
- 以下情况通常可以跳过 OpenSpec：错别字修正、窄范围文案编辑、一次性章节对齐修正、在已有规格变更后更新生成产物，以及不改变预期行为的小型测试期望更新。
- 需要 OpenSpec 时，应先创建或更新 proposal、design、tasks 和 spec delta，再进行大范围实现。OpenSpec 是持久设计记录，不要创建与其冲突的 Superpowers-only 最终设计文档。
- 如果 Superpowers 头脑风暴产出了有用的设计决策，将其总结进 OpenSpec 变更中。大范围实现前先取得人类对 OpenSpec 方向的批准，并让 OpenSpec tasks、specs 和 archive 状态与最终代码保持一致。
- Superpowers 回答“代理应该如何工作”。OpenSpec 回答“这个仓库应该做什么”。如果二者冲突，产品行为遵循仓库专用说明和 OpenSpec specs，执行方式遵循 Superpowers；当冲突会改变范围或预期行为时，询问用户。
- 不要只凭 OpenSpec 更新就声称完成；仍然需要实现和仓库专用验证。不要只凭 Superpowers 规划就声称完成；结果必须有测试和检查支撑。

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
