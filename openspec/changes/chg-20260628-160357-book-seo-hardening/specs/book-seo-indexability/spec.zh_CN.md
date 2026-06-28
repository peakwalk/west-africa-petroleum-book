## ADDED Requirements

### Requirement: Book output MUST publish crawlable discovery artifacts
站点构建完成后 MUST 生成根目录 `book-sitemap.xml`，列出 canonical 的英文和法文 book URL；同时还 MUST 生成在根目录引用该 sitemap 的 `robots.txt`。像 `chapters/front-matter.html` 这种仅用于跳转的页面 MUST NOT 出现在 sitemap inventory 中。

#### Scenario: Sitemap includes bilingual canonical book URLs
- **WHEN** `npm run build:site` 完成
- **THEN** `public/book-sitemap.xml` 存在
- **THEN** 其中包含 `https://upstreamatlas.com/book/`、`https://upstreamatlas.com/fr/book/` 以及这两个根路径下所有 canonical 内容页的绝对 URL
- **THEN** 它不会包含 `https://upstreamatlas.com/book/chapters/front-matter.html` 这类纯跳转页面

#### Scenario: robots.txt references the book sitemap
- **WHEN** `npm run build:site` 完成
- **THEN** `public/robots.txt` 存在
- **THEN** 它包含 `Sitemap: https://upstreamatlas.com/book-sitemap.xml`

### Requirement: Canonical book pages MUST publish unique canonical metadata
每个 canonical 的 book 落地页、章节页和参考页都 SHALL 发布非空 `<title>`、非空 `<meta name="description">` 和绝对 `<link rel="canonical">`。同一 locale 下的 canonical 页面之间 MUST NOT 共用重复的 title-and-description 组合。

#### Scenario: English chapter page emits unique absolute metadata
- **WHEN** 构建发布一个英文 canonical 章节页
- **THEN** 它的 `<head>` 中包含一个以 `| Upstream Atlas` 结尾的非空 `<title>`
- **THEN** 它的 description meta content 非空
- **THEN** 它的 canonical href 是一个绝对的 `https://upstreamatlas.com/book/...` URL

#### Scenario: French book landing page emits unique absolute metadata
- **WHEN** 构建发布 `https://upstreamatlas.com/fr/book/`
- **THEN** 它的 `<head>` 中包含非空 title 和非空 description
- **THEN** 它的 canonical href 等于 `https://upstreamatlas.com/fr/book/`

### Requirement: Canonical book landing pages MUST remain stable cover destinations
canonical 的 `/book/` 与 `/fr/book/` 落地页 SHALL 原地渲染封面体验，MUST NOT 一进入就通过客户端脚本自动跳到默认章节。封面上的显式 CTA MAY 继续链接到各 locale 预期的第一阅读章节。

#### Scenario: Book root stays on cover while preserving explicit reading entry
- **WHEN** 用户打开 `https://upstreamatlas.com/book/` 或 `https://upstreamatlas.com/fr/book/`
- **THEN** 已发布页面保持在封面路由本身，而不是自动前送到章节 URL
- **THEN** 封面 UI 仍然包含一个显式阅读 CTA，并链接到该 locale 对应的第一阅读章节

### Requirement: Canonical book pages MUST publish locale alternates only for equivalent pages
每个 canonical 的 book 页面都 SHALL 发布 self-referencing 的 `hreflang` 链接和一个 `x-default` 链接。只有存在已确认 EN/FR 对应关系的页面才 MUST 发布互相回指的 alternate；没有确认对应页的页面 MUST NOT 发布非等价 alternate 链接。

#### Scenario: Equivalent chapter pages emit reciprocal alternates
- **WHEN** 某个 canonical 英文章节页存在已确认的法文对应页
- **THEN** 英文页发布 `hreflang="en"`、`hreflang="fr"` 和 `hreflang="x-default"`
- **THEN** 对应的法文页发布 reciprocal 的 `hreflang="fr"` 与 `hreflang="en"`，并回指该英文页

#### Scenario: English-only pages keep self-reference plus x-default
- **WHEN** 某个 canonical 英文 book 页面不存在已确认的法文对应页
- **THEN** 该页面发布它自己的 `hreflang="en"` self-reference
- **THEN** 该页面发布一个指向自身 canonical URL 的 `hreflang="x-default"`
- **THEN** 该页面不会发布指向 `/fr/book/` 或其他非等价 URL 的法文 alternate

### Requirement: Canonical book pages MUST publish structured data appropriate to page type
book 落地页 SHALL 发布 `Book` JSON-LD。编号章节页 SHALL 发布 `Chapter` 与 `BreadcrumbList` JSON-LD。canonical 参考页 SHALL 发布 `WebPage` 与 `BreadcrumbList` JSON-LD。所有 structured-data URL 都 MUST 使用该页面自己的绝对 canonical URL。

#### Scenario: Book landing page emits Book schema
- **WHEN** 构建发布 `/book/`
- **THEN** 它的 `<head>` 中包含一个 `@type` 为 `Book` 的 `application/ld+json` block
- **THEN** schema 中包含该页面 canonical URL、`Upstream Atlas` publisher 信息以及双语语言 metadata

#### Scenario: Numbered chapter page emits Chapter and breadcrumb schema
- **WHEN** 构建发布一个编号章节页，例如 `/book/chapters/chapter-05-hydrocarbon-value-chain.html`
- **THEN** 它的 `<head>` 中包含 `Chapter` 与 `BreadcrumbList` 两种 structured data
- **THEN** 每个 schema entry 都使用该页面自己的绝对 canonical URL

#### Scenario: Reference page emits WebPage and breadcrumb schema
- **WHEN** 构建发布一个 canonical 参考页，例如 `/fr/book/chapters/glossary.html`
- **THEN** 它的 `<head>` 中包含 `WebPage` 与 `BreadcrumbList` 结构化数据
- **THEN** 它不会把这个页面错误标注成编号 `Chapter`

### Requirement: SEO hardening MUST preserve static crawlable chapter content
SEO hardening pass MUST 以“增量注入”为原则，MUST NOT 把章节正文挪到仅靠客户端 JavaScript 才能出现的位置。代表性的章节页在 SEO pass 执行之后，仍 SHALL 在静态 HTML markup 中保留章节标题和正文文本。

#### Scenario: Static chapter body remains visible after SEO injection
- **WHEN** 构建发布一个代表性的章节页
- **THEN** 生成后的 HTML 仍然包含该章节的 H1 和正文段落文本
- **THEN** 搜索引擎关键内容不会被延迟到客户端脚本执行后才可见
