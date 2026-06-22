# 新英文替换基线

## 证据来源

- 新英文 DOCX：`resources/Exploration et exploitation des ressources pétrolières en Afrique de 1 (EN).docx`
- 新英文 PDF：`resources/Exploration et exploitation des ressources pétrolières en Afrique de 1 (EN).pdf`
- 当前英文 alias 指向的旧 DOCX：`resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).docx`
- 当前英文 alias 指向的旧 PDF：`resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).pdf`
- 当前英文发布导航源：`editions/en/content/SUMMARY.md`
- 当前法文发布导航冻结边界：`editions/fr/content/SUMMARY.md`

从当前工作区提取到的量化信号：

- 旧英文 DOCX 大小：`11,274,269` bytes
- 新英文 DOCX 大小：`83,721,583` bytes
- 旧英文 PDF 大小：`10,094,932` bytes
- 新英文 PDF 大小：`144,993,188` bytes
- 旧英文非空段落数：约 `1,074`
- 新英文非空段落数：约 `9,135`
- 通过 caption 风格段落扫描得到的新英文 figure 数：`80`
- 通过 caption 风格段落扫描得到的新英文 table 数：`33`

解释：

- 新英文稿不是当前英文版的修订稿，而是一本体量和结构都显著不同的新书。
- 当前英文 parity 假设已经失效。执行 `python3 scripts/check_docx_parity.py --edition en --docx <replacement-docx>` 时，目前会对每个英文章节都提取出 0 个 outline/body blocks。

## 新英文稿结构

### 前置材料清单

在 heading-1 章节序列开始之前，新英文稿暴露出如下 pre-body materials：

1. 标题页
   - `Exploration and Production of Petroleum Resources in West Africa: Roles and Responsibilities of Governments and Analysis of Fiscal Regimes`
2. `DISCLAIMER`
3. `Preface`

在提取结果中未发现的独立前置章节：

- 独立的 `Foreword`
- 独立的 `Abbreviations, Acronyms and Abbreviations`
- 独立的 manuscript `List of Figures`
- 独立的 manuscript `List of Tables`

对 reader 侧的含义：

- `list-of-figures.md` 与 `list-of-tables.md` 可以继续保留为 synthetic 的 web reference pages，但不应再被当作 manuscript-native 的前置章节。

### 顶层章节清单

新英文稿暴露出 12 个 heading-1 sections：

1. `General Introduction`
2. `Emerging Petroleum Provinces in West Africa`
3. `West Africa Country Analysis`
4. `National Oil Companies in West Africa`
5. `Hydrocarbon Value Chain`
6. `Upstream Operations and Government Roles`
7. `Petroleum Fiscal Regimes`
8. `West African Fiscal Regimes`
9. `Socio-Political Determinants`
10. `Petroleum Data Management in West Africa`
11. `General Conclusion`
12. `Vision for West Africa 2050`

原始 DOCX 的 TOC 样式在 `8.*` 与 `10.*` 之间存在编号跳跃。由于 heading-1 序列本身是连续的，这个跳跃被视为 manuscript-style normalization issue，而不是发布阻塞项。后续实现应优先依据 heading 分析，而不是盲信原始 TOC 编号。

### 后置材料清单

在 12 个编号化正文章节之后，新英文稿继续给出：

1. `Glossary`
2. `Bibliographical References`

对 reader 侧的含义：

- `General Conclusion` 与 `Vision for West Africa 2050` 属于编号化正文，而不是 web-only back matter。

## 旧到新的主题映射

当前英文树与新英文稿不是一一对应关系。迁移基线如下：

| 当前英文源 | 新英文稿目标 | 迁移说明 |
| --- | --- | --- |
| `cover.md` | synthetic title-page wrapper | 保留为 reader 对标题页的包装层。 |
| `list-of-figures.md` | synthetic web figure index | 保留为 reader utility，并重建内部引用；即使 manuscript 本身没有暴露独立 figures chapter。 |
| `list-of-tables.md` | synthetic web table index | 保留为 reader utility，并重建内部引用；即使 manuscript 本身没有暴露独立 tables chapter。 |
| `abbreviations-acronyms-and-abbreviations.md` | 暂未发现独立对应章节 | 默认退役，除非后续人工审稿发现隐藏附录。 |
| `foreword.md` | 暂未发现独立对应章节 | 退役。新稿使用 `DISCLAIMER` 和 `Preface`，而不是独立 foreword。 |
| `general-introduction.md` | `General Introduction` | 内容保留，但 slug 会迁入编号化的正文章节命名空间。 |
| `chapter-01-value-chain-of-the-hydrocarbon-sector.md` | `Hydrocarbon Value Chain` | 主题保留，但标题与内部结构变化很大。 |
| `chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md` | `Upstream Operations and Government Roles` | 主题保留，但范围扩大且标题改变。 |
| `chapter-03-tax-regimes-in-the-petroleum-sector.md` | `Petroleum Fiscal Regimes` | 主题保留，但内部重组明显。 |
| `chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md` | `West African Fiscal Regimes` | 主题保留，但国家覆盖和建模内容扩大。 |
| `chapter-05-key-socio-political-determinants-of-oil-sector-performance.md` | `Socio-Political Determinants` | 主题保留，但结构更新。 |
| `chapter-06-west-africa-in-depth-country-analysis.md` | `West Africa Country Analysis` | 主题保留，但国家集合更大，内部布局也变了。 |
| `general-conclusion.md` | `General Conclusion` | 内容保留，但 slug 会迁入编号化的正文章节命名空间。 |
| `glossary.md` | `Glossary` | 保留现有语义化 slug，并用新稿内容替换正文。 |
| `bibliographical-references.md` | `Bibliographical References` | 保留现有语义化 slug，并用新稿内容替换正文。 |

只存在于新稿中的新增主题：

- `DISCLAIMER`
- `Emerging Petroleum Provinces in West Africa`
- `National Oil Companies in West Africa`
- `Petroleum Data Management in West Africa`
- `Vision for West Africa 2050`

## 仅英文切换边界

### 本次变更允许修改的范围

预计会变更的文件或区域：

- `editions/en/content/SUMMARY.md`
- `editions/en/content/index.md`
- `editions/en/content/chapters/**`
- `editions/en/content/images/**`
- `editions/en/locale.json`
- `resources/editions/en/reference.docx`
- `resources/editions/en/reference.pdf`
- `scripts/docx_parity/**`
- `scripts/check_docx_parity.py`
- `scripts/build_docx_figure_manifest.py`
- `scripts/check_docx_figures.py`
- `scripts/render_pdf_figures.py`
- `scripts/render_docx_chart_figures.py`
- `scripts/render_docx_shape_figures.py`
- `scripts/render_docx_vector_figures.py`
- `scripts/build_reader_page_meta.mjs`
- `scripts/build_static_reader_sidebar.mjs`
- `scripts/generate-chapters-page.mjs`
- `theme/custom.js`
- `theme/custom.css`
- 所有把旧英文章节拓扑写死的 English-facing tests 和 assertions

### 本次变更明确冻结的范围

以下路径是显式 no-touch boundary：

- `editions/fr/**`
- `resources/editions/fr/reference.docx`
- `resources/editions/fr/reference.pdf`

允许修改共享脚本，但前提是这些修改仅用于解析或发布新的英文版。任何共享脚本变更后，都必须补跑最小法文回归检查，因为法文文件本身保持冻结。

## 目标英文 slug 集合

本次变更对 front matter 保留语义化 slug，但对编号化 manuscript sections 继续保留 `chapter-` 前缀契约，因为当前 parity、figure、reader-meta 和 chapter-library 工具链都把 `chapter-*` 文件视为 canonical body-chapter 集合。原始 TOC 的编号跳跃会被归一化为基于 heading-1 顺序的连续章节序列。

计划中的英文章节文件：

- `chapters/cover.md`
- `chapters/disclaimer.md`
- `chapters/preface.md`
- `chapters/list-of-figures.md`
- `chapters/list-of-tables.md`
- `chapters/chapter-01-general-introduction.md`
- `chapters/chapter-02-emerging-petroleum-provinces-in-west-africa.md`
- `chapters/chapter-03-west-africa-country-analysis.md`
- `chapters/chapter-04-national-oil-companies-in-west-africa.md`
- `chapters/chapter-05-hydrocarbon-value-chain.md`
- `chapters/chapter-06-upstream-operations-and-government-roles.md`
- `chapters/chapter-07-petroleum-fiscal-regimes.md`
- `chapters/chapter-08-west-african-fiscal-regimes.md`
- `chapters/chapter-09-socio-political-determinants.md`
- `chapters/chapter-10-petroleum-data-management-in-west-africa.md`
- `chapters/chapter-11-general-conclusion.md`
- `chapters/chapter-12-vision-for-west-africa-2050.md`
- `chapters/glossary.md`
- `chapters/bibliographical-references.md`

说明：

- `cover.md` 继续保留，但它会变成对 manuscript 标题页的 synthetic reader wrapper，而不是旧意义上的 `Cover` TOC 项。
- `disclaimer.md` 与 `preface.md` 来自 manuscript-native front matter。
- `list-of-figures.md` 与 `list-of-tables.md` 保留为 synthetic 的 web utilities，而不是 manuscript-native 章节。
- 编号化 manuscript sections 会迁入连续的 `chapter-XX-...` 命名空间，这样 batch parity、figure inventory 和 reader metadata 仍能在不引入第二套正文发现逻辑的前提下工作。
- `glossary.md` 与 `bibliographical-references.md` 保留为语义化 back-matter slugs，因为新稿在编号化正文之后仍然保留了这两个参考章节。

## 本次变更的 deep-link 策略

决策：

- 只保留那些仍然对应真实或 synthetic replacement front-matter section 的 deep links：
  - `cover.html`
  - `disclaimer.html`
  - `preface.html`
  - `list-of-figures.html`
  - `list-of-tables.html`
  - `glossary.html`
  - `bibliographical-references.html`
- 有意打断那些指向已退役 section name 或旧章节编号的 legacy English deep links，包括：
  - `abbreviations-acronyms-and-abbreviations.html`
  - `foreword.html`
  - `general-introduction.html`
  - `general-conclusion.html`
  - `chapter-01-value-chain-of-the-hydrocarbon-sector.html`
  - `chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html`
  - `chapter-03-tax-regimes-in-the-petroleum-sector.html`
  - `chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html`
  - `chapter-05-key-socio-political-determinants-of-oil-sector-performance.html`
  - `chapter-06-west-africa-in-depth-country-analysis.html`

原因：

- 如果继续保留这些 legacy paths，就等于让已退役的六章拓扑以兼容壳的形式继续存在，这与“以新稿为唯一真源”的设计直接冲突。
- 连续的 `chapter-XX-...` slug 在保留现有 body-chapter 工具链契约的同时，也仍然丢弃了已退役的六章拓扑。
- 如果后续确实需要 legacy redirect handling，应该在新的英文结构稳定后，以单独的显式兼容层来实现。
