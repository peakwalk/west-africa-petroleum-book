## Context

仓库已经按 edition root 分离了英文和法文，但当前英文版仍然体现的是旧英文稿的信息架构。现在放进 `resources/` 的新英文 DOCX/PDF 在范围和布局上都与当前英文发布版有本质差异。

当前工作区可观察到的证据：

- 旧英文 DOCX 约 11.3 MB、约 1,074 个非空段落；新英文 DOCX 约 83.7 MB、约 9,135 个非空段落。
- 当前英文 `SUMMARY.md` 发布的是 6 个正文主章节加 front/back matter；而新英文稿暴露出的顶层结构至少有 12 个 heading-1 section，从 `General Introduction` 一直到 `Vision for West Africa 2050`，外加 disclaimer/preface/list 等前置或列表内容。
- 执行 `python3 scripts/check_docx_parity.py --edition en --docx 'resources/Exploration et exploitation des ressources pétrolières en Afrique de 1 (EN).docx'` 时，当前每个英文章节都会报 `outline.entry_count_mismatch`、`body.block_count_mismatch` 和 `body.sequence_mismatch`，且提取到的 DOCX outline/body 计数都是 `0`，这证明旧的英文章节锚点模型不能原样复用。

因此，这不是“章节刷新”问题，而是一个“英文版重建”问题，并且有两个固定约束：

1. 英文 canonical source 必须切换到新的英文稿；
2. 法文版必须保持现有导航、内容、figure assets 和 manuscript aliases 不变。

## Goals / Non-Goals

**Goals:**
- 以新的英文稿替换英文版，并将其作为唯一的 canonical English source。
- 重建英文导航、章节拓扑和配套内容，使发布后的英文书与新英文稿一致，而不是继续套用旧的六章壳子。
- 保持法文版在 source ownership、导航、内容、figure assets 和 manuscript aliases 上不变。
- 让英文切换支持 staged validation，在 canonical English alias 切换前就能跑校验。
- 保留一条只影响英文的 rollback path，恢复旧版时不需要任何法文改动。

**Non-Goals:**
- 把新英文稿的改动同步翻译到法文版。
- 保留已退役的英文六章导航，或强行把新英文稿塞进旧 slug tree。
- 手工修改 `public/` 输出，或绕开既有 edition build pipeline。
- 解决所有未来多语言分歧问题，超出当前英文替换所必需的范围。

## Decisions

### 1. 把新英文稿视为一次完整替换，而不是增量覆盖

第一性原理是：canonical English book 的真源是 manuscript，而不是当前 Markdown 树。由于新稿在体量、章节体系和导航语义上都变了，迁移必须从新稿出发，围绕它重建英文版。

备选方案：
- 原地覆盖当前英文各章节，同时保留旧结构。否决，因为这会保留一个误导性的英文 sidebar，并且必然长期产生 manuscript 与 published book 的 parity 漂移。

### 2. 延迟英文 alias 切换，直到重建后的内容通过校验

仓库已经有 `resources/editions/en/reference.docx` 和 `reference.pdf` 这层很有价值的间接层。重建期间，这两个英文 alias 应继续指向旧稿；校验时通过显式 `--docx` 与 `--pdf` 参数指向新英文源文件，直到重建后的英文内容、figure assets 和 manifest 都准备好。

这样可以把 manuscript cutover 和 content reconstruction 分离开：

- 重建工作可以继续推进，但不会破坏当前英文发布基线；
- 最终 alias 变更会变成一个明确的 release step；
- rollback 只需要一次很小的英文 alias 回退，加上对英文内容/资源的 Git restore。

备选方案：
- 先改英文 alias，再回头修内容树。否决，因为这会立刻让英文 parity 校验针对一个已知陈旧的内容树整体失效。

### 3. 基于新稿重建英文导航，并允许英文拓扑与法文独立分叉

英文左侧导航必须依据新英文稿的真实结构重新生成。这意味着：

- 重写 `editions/en/content/SUMMARY.md`；
- 重新定义 `editions/en/content/chapters/` 下的英文章节文件集合；
- 围绕新稿中的 disclaimer、preface、编号化正文、glossary 与 bibliographical references 重新划分 front matter 与 back matter，并把 figures/tables 索引视为 synthetic 的 web utilities，而不是 manuscript-native 章节。

法文版则保持当前的 `SUMMARY.md` 和章节集合不变。对于这次变更来说，真正的 invariant 不再是“英法结构对称”，而是“各 edition 相互隔离”。

备选方案：
- 继续让英文和法文导航树保持镜像。否决，因为用户已经明确要求法文不变，而新英文书也已经不再与法文书保持结构平行。

### 4. 按 4 条 MECE 迁移轨道拆分工作

为了避免执行时互相缠绕，本变更应该拆成 4 条互不重叠的工作流：

1. **结构与锚点**：chapter inventory、`SUMMARY.md`、parser rules、front/back matter 边界。
2. **叙事内容**：英文章节 Markdown、标题、列表、免责声明和 reader-facing copy。
3. **图表与表格**：figure inventory、manifest、rendered assets、references 和 retirements。
4. **发布安全**：alias cutover、回归检查、rollback procedure 和 change notes。

这是符合 MECE 的边界划分，能够防止把内容决策偷偷埋进资源或校验工作里。

备选方案：
- 一次性 bulk-convert 全部内容，失败了再回头修。否决，因为这会把 source-structure、figure 和 release-cutover 三种不同错误混进同一个故障域。

### 5. 在大规模重写内容前，先让英文 parity pipeline 认识新结构

当前英文 parity 的失败模式说明 `scripts/docx_parity/extract_docx.py` 及相关逻辑仍然假设旧稿的锚点模型。提取/parity 层必须先学会识别新稿的章节边界和配套材料，后续重建后的英文内容才能做增量校验。

落地上意味着：

- 新增或收紧针对新英文稿的 chapter boundary rules；
- 在 alias cutover 之前就允许 checker 校验新的英文结构；
- 对 parser 的共享改动后，继续用法文回归检查保护法文提取行为不变。

备选方案：
- 跳过 parity，只靠人工 review 加 `mdbook build`。否决，因为本次最大风险正是 manuscript 与 content 的漂移，而 parity 正是用来控制这个问题的；范围也太大，不能只靠人工核对。

### 6. 把法文版冻结为显式的 regression boundary

法文版不只是“这次不做”，而是这次变更的保护边界。实施时应默认：

- 不改 `editions/fr/**`；
- 不改 `resources/editions/fr/reference.*`；
- 任何共享 parser 或 build-script 的变更后，都要补跑最小法文回归检查。

备选方案：
- 为了未来一致性，顺手把英文结构变更传播到法文树。否决，因为这直接违反用户约束，并且只会扩大风险面，并不能解决当前问题。

### 7. 新英文 raster figure 采用 PNG + WebP 双产物发布，并坚持 PDF 优先、单图 DOCX 回退

对于新的英文稿，稳定的 figure 标识是 figure number，而不是它在源文件里的封装格式。因此，raster figures 应发布为“同编号 PNG sidecar + 同编号 WebP”：

- `figure-NNN.png` 保持为稳定导出物，也便于回滚和人工核对；
- 当 `png` 和 `webp` 同时存在时，`figure-NNN.webp` 作为 chapter markdown 与 figure manifest 的 canonical web-facing asset。

渲染路径仍然以 PDF 为第一选择，以保证版式保真。但新英文稿里存在已经在 DOCX 内压平的 bitmap figure，且至少有一个会让 PDF 白底区域检测失败。对于这类“PDF 裁切失败，但在 DOCX 中仍然只有一个内嵌 bitmap 源”的英文新版 figure，pipeline 应对该 figure number 回退到 DOCX bitmap 提取，而不是让整个批次失败。

备选方案：
- 继续让新英文 raster figure 只发布 PNG。否决，因为这会降低网页交付效率，也会让章节引用偏离仓库既有的 WebP-first 发布模式。
- 只要有一个 replacement-English bitmap 不能自动 PDF 裁切，就让整个批次失败。否决，因为这会让单个检测边界条件阻塞整批发布，而实际上仍然存在安全的单图 DOCX 回退路径。

## Risks / Trade-offs

- [新稿 TOC 样式不完全一致，原始提取里在 8 到 10 之间存在明显编号跳跃] -> 不直接信任原始 TOC 文本，而是结合 heading analysis 与人工审稿来归一化结构。
- [部分英文图号可能沿用旧 figure number，但底层布局已经变了] -> 把 figure-number reuse 视为内容变化，从新稿重建英文 manifest，并重渲染变化资源，而不是假设资源可复用。
- [旧英文 chapter URL 可能与新导航树不再对应] -> 在重写 `SUMMARY.md` 前先明确并记录 cutover 后的 deep-link policy；如果需要兼容，就把 redirect 或 tombstone 处理作为单独显式任务。
- [共享 parser 变更可能意外影响法文版] -> 即使法文文件被冻结，也要在 parser 变更后补跑最小法文 parity 和 figure regression checks。
- [延迟 alias 切换意味着实现期间分支里会同时存在“旧 alias + 新候选内容”] -> 接受这个暂时的双态，因为它能显著降低发布风险，并让回滚保持简单。

## Migration Plan

1. 把新英文稿的顶层结构、front matter、back matter 和 figure inventory 固化为这次变更的基线证据。
2. 更新英文 DOCX extraction/parity workflow，使其在英文 alias 仍指向旧稿时，也能通过显式 `--docx`/`--pdf` 参数解析新稿。
3. 重写英文 `SUMMARY.md`、章节文件和任何依赖英文章节结构的 reader-facing metadata，使之匹配新稿的信息架构。
4. 基于新的英文 DOCX/PDF 重建英文 figure manifest 和已发布 figure assets，然后更新 chapter references 并移除已退役资源。
5. 把 `resources/editions/en/reference.*` 指向新英文源文件，并执行最小必要的英文发布检查和法文回归检查。

Rollback strategy：

- 把 `resources/editions/en/reference.docx` 和 `reference.pdf` 恢复到旧稿目标；
- 从 Git 恢复 `editions/en/content/**` 和英文 figure assets；
- 不触碰 `editions/fr/**` 或 `resources/editions/fr/**`。

## Open Questions

- 在新的英文导航树定稿后，旧的英文章节 deep link 是否需要兼容处理，还是可以接受英文章节 URL 集合随新稿一起改变？
- 原始提取中新稿在 `8.*` 与 `10.*` 之间看似缺失的顶层 section，到底是真正的编辑性合并，还是一个需要在提取阶段归一化的 DOCX 样式缺陷？
