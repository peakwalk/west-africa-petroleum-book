## Why

当前双语 book 输出已经是可抓取的 HTML，但生成后的 `/book/` 与 `/fr/book/` 仍然存在 book 页面 description 为空、缺少绝对 canonical URL、没有结构化数据、也没有专门的 sitemap 或 `robots.txt` 引用等问题。现有跨语言页面映射是为 reader 导航服务的，不是为 SEO 等价页服务的，因此会把未翻译的英文页错误地指向法文首页，而不是正确地省略非等价 `hreflang`。当前 reader shell 还会把 `/book/` 自动前送到默认阅读章节，导致侧边栏里的 `Cover` 实际上不能停留在封面页。

UA-10 要求把整本书作为一级搜索入口来做可索引性加固，同时第一阶段先覆盖英文版并保留现有双语 reader shell。为此需要现在就把 SEO hardening 做成 repo 自己维护的构建后步骤，让 Search Console 提交和后续重建都依赖稳定的发现工件与页面级 metadata，而不是一次性的人工修补。

## What Changes

- 为生成后的双语 book 输出增加一个构建后 SEO hardening 步骤，使 `/book/`、`/fr/book/` 以及 canonical 的章节/参考页都具备唯一 title、非空 description、绝对 canonical URL、`hreflang`、`x-default` 和结构化数据。
- 让 `/book/` 和 `/fr/book/` 保持为稳定的封面落点，把进入正文的动作留给 `Start reading` / `Commencer la lecture` 这类显式 CTA。
- 生成根目录 `book-sitemap.xml`，覆盖 canonical 的英文和法文 book URL，并生成在根目录引用该 sitemap 的 `robots.txt`。
- 将 reader 语言导航回退逻辑与 SEO alternate-page 等价映射拆开；只有真实存在 EN/FR 对应关系的页面才发布 reciprocal `hreflang`，没有对应法文页的英文页只保留 self-reference 与 `x-default`。
- 增加构建期防回归覆盖；一旦 sitemap 覆盖、metadata 唯一性、canonical URL、结构化数据或语言 alternate 规则漂移，就让测试直接失败。

## Capabilities

### New Capabilities
- `book-seo-indexability`: 构建后的双语 book 输出可以在不依赖部署后人工修补的前提下，稳定发布可抓取的发现工件和页面级 SEO 信号，覆盖落地页、章节页和参考页。

### Modified Capabilities
- None.

## Impact

- 受影响的构建脚本预计包括 `scripts/build_site.mjs`、`scripts/build_reader_page_meta.mjs`，以及新增的 `scripts/` 或 `scripts/shared/` 下 SEO/sitemap helper。
- 受影响的 reader 本地化逻辑包括 `scripts/localize_reader_shell.mjs` 中当前的跨语言映射；它需要拆分为导航职责和 SEO 职责。
- 受影响的 reader 行为逻辑还包括 `theme/custom.js`，它必须停止把图书首页自动前送到默认章节。
- 受影响的测试包括 `tests/test_book_editions.py`、`tests/test_reader_page_meta.py` 与 `scripts/test-site-render.sh` 这类 metadata / site build 断言。
- 重建后受影响的生成产物包括 `public/book/**`、`public/fr/book/**`、`public/book-sitemap.xml` 和 `public/robots.txt`。
- 不引入新的运行时依赖。
