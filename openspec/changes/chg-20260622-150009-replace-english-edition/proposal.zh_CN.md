## Why

新加入的英文稿并不是当前英文版的小修小补，而是一本替代旧版的新书。它的正文体量更大，左侧导航结构不同，章节体系也不同。当前英文工作区仍然编码了已退役的六章结构，而 `python3 scripts/check_docx_parity.py --edition en --docx <new-manuscript>` 目前会对每个英文章节都报出提取到的 outline/body 为 0，这说明旧锚点模型已经无法匹配新的源稿。

因此需要先形成一个受控的“仅英文替换”方案，让仓库可以把新英文稿升级为新的 canonical source，同时不修改法文版。法文的导航、内容、图表和 manuscript alias 在整个变更过程中都必须保持不变。

## What Changes

- 将新的英文 DOCX/PDF 作为仅供英文版使用的候选 canonical manuscript，同时保持法文 manuscript alias 与法文内容不变。
- 基于新英文稿真实的目录结构，重建英文 `SUMMARY.md`、章节树、front matter、back matter 和 reader sidebar，而不是继续保留已退役的六章壳子。
- 更新英文 DOCX parity / extraction 流程，使校验逻辑能够识别新的英文章节锚点、前置材料和后置材料。
- 依据新的英文稿重新生成英文 figure inventory、figure manifest 与已发布图表资源，并移除那些只存在于旧英文稿中的 legacy figures。
- 仅在分阶段校验通过后切换英文 manuscript alias，并保留一条只影响英文、不触碰法文文件的回滚路径。

## Capabilities

### New Capabilities
- `english-edition-replacement`: 以新的 canonical manuscript 替换英文版，重建英文导航、章节内容和图表资源，同时保持法文版不变。

### Modified Capabilities
- None.

## Impact

- 预计会影响 `config/editions.json`、`resources/editions/en/reference.docx`、`resources/editions/en/reference.pdf`、`editions/en/content/SUMMARY.md`、`editions/en/content/chapters/*`、`editions/en/content/images/*`，以及 `scripts/docx_parity/*`、`scripts/check_docx_parity.py`、`scripts/build_docx_figure_manifest.py` 和 figure render helpers 这类共享校验/构建脚本。
- 本变更明确不包含对 `editions/fr/**`、`resources/editions/fr/reference.*` 和法文 reader 导航/内容的修改。
- 构建与校验工作会聚焦英文切换安全和共享解析器变更带来的法文回归保护；不引入新的运行时依赖。
