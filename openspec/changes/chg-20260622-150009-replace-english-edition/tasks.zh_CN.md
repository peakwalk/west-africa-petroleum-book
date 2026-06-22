## 1. 冻结边界并盘点新英文稿

- [x] 1.1 把新英文稿的 TOC、front matter、back matter、figure/table 数量以及旧主题到新主题的映射固化为 change-local evidence，确保迁移范围是显式的。
- [x] 1.2 记录“仅英文切换”的边界：允许变更的 `editions/en/**`、`resources/editions/en/reference.*` 和共享 parser/build scripts，以及必须保持不变的 `editions/fr/**` 与 `resources/editions/fr/**`。
- [x] 1.3 根据新英文稿确定目标的英文章节/file slug 集合，并在开始内容编辑前记录任何对 legacy deep links 的有意破坏。

## 2. 先让 parity 和 extraction pipeline 理解新的英文结构

- [x] 2.1 更新 `scripts/docx_parity/extract_docx.py` 及相关 helpers，使其识别新英文稿的 front matter、chapter markers 和 back-matter anchors，而不是继续依赖已退役的六章模型。
- [x] 2.2 新增或更新针对性的 parity tests/fixtures，使 `python3 scripts/check_docx_parity.py --edition en --docx <replacement-docx>` 能提取到真实的 outline/body content，而不是整章都是 0-block。
- [x] 2.3 在英文章节解析器改动后，补跑最小法文 parity 回归检查，确保法文提取行为不变。

## 3. 基于新英文稿重建英文导航与章节 Markdown

- [x] 3.1 重写 `editions/en/content/SUMMARY.md`，使其匹配新英文稿的信息架构，包括 front matter、重命名/重排后的章节和 back matter。
- [x] 3.2 用从新稿导出的章节集合替换 `editions/en/content/chapters/` 下当前的英文章节 Markdown 文件，并在 manuscript 暴露出来时妥善处理 disclaimer/preface。
- [x] 3.3 更新任何依赖英文章节结构或书名的 English landing / reader metadata，确保左侧导航与配套页面和新英文稿保持一致。

## 4. 收敛英文图表、manifest 和章节引用

- [x] 4.1 依据新的英文 DOCX/PDF 重建英文 figure inventory 和 `editions/en/content/images/figure-manifest.json`。
- [x] 4.2 通过正确的 pipeline（`render:pdf-figures`、`render:docx-chart-figures`、`render:docx-shape-figures`、`render:docx-vector-figures`）重渲染所有变化的英文 figures，并从已发布英文树中移除已退役的英文字图资源。
- [x] 4.3 更新英文章节中的 figure references、captions 和 figure-related render assertions，使已发布英文内容与 asset inventory 与新稿一致。
- [x] 4.4 对新英文 raster figures 保留同编号 `png` 导出，同时生成配套 `webp` 供网页交付；当某个请求的 figure 在 PDF 裁切失败但仍然只有单个 DOCX bitmap 源时，允许回退到 DOCX 单图提取。

## 5. 切换英文 aliases 并验证发布

- [x] 5.1 仅在英文内容与图表已经通过显式 manuscript path 校验后，才把 `resources/editions/en/reference.docx` 与 `resources/editions/en/reference.pdf` 指向新的英文源文件。
- [x] 5.2 为 cutover 执行最小必要发布检查：`python3 scripts/check_docx_parity.py --edition en`、`python3 scripts/check_docx_figures.py --edition en`、`npm run build:site`、定向 site tests，以及法文回归检查。
- [x] 5.3 在 change notes 中记录 rollback procedure，并确认只需回退英文 aliases 和 `editions/en/content/**` 就可以恢复旧英文发布，而不需要任何法文变更。
