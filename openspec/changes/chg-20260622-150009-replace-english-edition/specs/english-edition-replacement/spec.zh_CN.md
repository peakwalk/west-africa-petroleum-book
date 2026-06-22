## ADDED Requirements

### Requirement: English replacement MUST preserve French edition immutability
仓库 MUST 支持替换英文 manuscript、导航、内容和 figure assets，同时不修改法文的 summary structure、chapter files、figure assets 和 French manuscript aliases。

#### Scenario: English alias cutover leaves French manuscript aliases untouched
- **WHEN** 英文替换最终完成
- **THEN** 只有 `resources/editions/en/reference.docx` 和 `resources/editions/en/reference.pdf` 的目标发生变化，而 `resources/editions/fr/reference.docx` 与 `resources/editions/fr/reference.pdf` 保持不变

#### Scenario: English content rebuild leaves French navigation unchanged
- **WHEN** 为替换发布而重写英文 `SUMMARY.md` 与英文章节文件
- **THEN** `editions/fr/content/SUMMARY.md` 与 `editions/fr/content/chapters/*` 在同一个 change set 中保持不变

### Requirement: English navigation MUST be regenerated from the replacement manuscript topology
英文版 MUST 从新的英文 manuscript 的真实 front matter、top-level sections 和 back matter 推导自己的 `SUMMARY.md`、chapter inventory 和 reader sidebar。当已退役的六章英文拓扑与 manuscript 不再匹配时，MUST NOT 再把它保留为兼容壳层。

#### Scenario: English summary matches the replacement manuscript structure
- **WHEN** 为替换发布生成 English summary
- **THEN** 它列出的必须是新稿的 front matter 和 top-level section 顺序，而不是旧的六章大纲

#### Scenario: English parity no longer extracts zero content blocks
- **WHEN** 英文切换后运行 `python3 scripts/check_docx_parity.py --edition en`
- **THEN** 英文章节集合使用新稿的锚点从 replacement manuscript 中提取，且不会再对每个章节都报告提取到的 outline/body block 为 0

### Requirement: English content and figures MUST converge to the replacement manuscripts
英文版 MUST 依据新的英文 DOCX/PDF 重建 chapter Markdown、figure manifests 和 published figure assets。凡是只存在于旧英文稿中的 legacy English figures 或 chapter text，在发布前 MUST 从已发布英文集合中移除。

#### Scenario: English figure manifest is built from the replacement manuscript
- **WHEN** 为替换发布执行 `python3 scripts/build_docx_figure_manifest.py --edition en`
- **THEN** 生成的 manifest 反映的是新英文稿的 figure inventory 和 published asset paths

#### Scenario: 新英文 raster figures 同时保留编号 PNG 导出和 canonical WebP 引用
- **WHEN** 基于新的英文 DOCX/PDF 重建英文 raster figures
- **THEN** 每个 figure 都保留同编号的 `figure-NNN.png` 导出，同时生成对应的 `figure-NNN.webp` 用于网页交付；当两者同时存在时，manifest 与 chapter markdown 引用 `webp`

#### Scenario: Retired English-only material does not survive cutover
- **WHEN** 某个 figure 或 chapter section 只存在于旧英文稿中
- **THEN** cutover 后，它不会出现在已发布的英文 markdown 和 asset tree 中

### Requirement: English cutover MUST use staged validation and rollback
在 canonical English aliases 切换之前，英文替换 MUST 先针对新的 manuscripts 通过校验。最终 cutover MUST 能够通过恢复旧英文 alias targets 和 English content tree 的 Git 状态来回滚，而且整个过程不能修改任何法文文件。

#### Scenario: Pre-cutover validation can run without alias switch
- **WHEN** 新的英文内容仍在构建中
- **THEN** parity 与 figure-validation 命令可以通过显式参数直接指向新的 English DOCX/PDF，而 canonical English aliases 仍然指向旧稿

#### Scenario: English rollback is English-only
- **WHEN** 新的英文发布需要回滚
- **THEN** rollback 会恢复旧的 English alias targets 和 English content/figure files，而不会触碰法文 summary、法文章节或法文 figure assets

### Requirement: Reader entry and cross-edition links MUST follow the active edition topology
替换英文版之后，reader 入口路由和语言切换链接 MUST 基于当前 edition 的真实页面拓扑来解析，不能再假设英文与法文共享同一组 slug。另一种语言中如果没有足够接近的对应页面，链接 MUST 回退到对端 reader 首页，而不是继续指向不存在的章节路径。

#### Scenario: English and French reader homes keep different first readable pages
- **WHEN** 读者打开英文 `/book` 或法文 `/fr/book`
- **THEN** 英文进入 `chapters/disclaimer.html`，而法文继续进入 `chapters/foreword.html`

#### Scenario: Unique English pages do not generate dead French links
- **WHEN** 读者从英文独有页面（例如 `disclaimer.html`、`preface.html` 或没有明确法文对应页的新英文章节）使用语言切换
- **THEN** 切换链接指向 `/fr/book/?lang=fr`，而不是不存在的 `/fr/book/chapters/<same-slug>.html`

#### Scenario: Topic-equivalent pages keep direct cross-edition links
- **WHEN** 读者从主题上存在明确对应关系的页面使用语言切换
- **THEN** 切换链接直接指向映射后的对端页面，例如英文 `chapter-05-hydrocarbon-value-chain.html` 直接链接到法文 `chapter-01-value-chain-of-the-hydrocarbon-sector.html`
