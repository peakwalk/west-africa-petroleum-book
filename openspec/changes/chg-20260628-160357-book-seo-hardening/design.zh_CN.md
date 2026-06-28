## Context

当前站点构建链本来就把 book 输出当作“构建后再加工的产物”，而不是纯粹的 mdBook 直出。`scripts/build_site.mjs` 会先构建每个 edition，然后继续执行 `build_reader_page_meta.mjs`、`build_static_reader_sidebar.mjs`、`localize_reader_shell.mjs` 等 repo 自己维护的 post-build 步骤。

这正是放置 SEO hardening 的合适层级，因为最终生成的 HTML 已经包含了 mdBook 模板单独拿不到的信息：双语 route prefix、章节间的跨语言对应关系、提取后的 lede，以及根目录输出路径。一次本地重建已经确认当前缺口：`/book/` 和 `/fr/book/` 的 `meta name="description"` 为空，没有 canonical、没有 JSON-LD，也没有根目录级别的 `robots.txt` 和 `book-sitemap.xml`。

这里还有一个语言映射正确性约束。`scripts/localize_reader_shell.mjs` 现在用一个 `CROSS_LOCALE_PAGE_MAP` 同时服务 reader 导航，其中一部分英文独占页面会故意回退到 `/fr/book/`。这对于 UI 语言切换可以接受，但对于 SEO alternate 不可接受，因为 `hreflang` 只能连接真实等价页。

## Goals / Non-Goals

**Goals:**
- 为双语 canonical 的 book 落地页、章节页和参考页发布稳定的 SEO metadata。
- 让 `/book/` 和 `/fr/book/` 稳定停留在封面页，使 canonical 图书根路径与 reader 中的 `Cover` 导航目标保持一致。
- 生成专门的 `book-sitemap.xml`，并在根目录 `robots.txt` 中引用它。
- 确保 `hreflang` 只声明真实存在的 EN/FR 对应页；没有法文对应页的英文页只保留 self-reference 与 `x-default`。
- 在尽量复用现有构建期 metadata 提取逻辑的前提下，保持章节正文仍然以静态 HTML 发布、可被抓取。

**Non-Goals:**
- 修改章节正文、翻译范围，或 canonical 路由路径；本次只移除图书首页到默认章节的客户端自动前送。
- 自动化 Google Search Console 提交。
- 重做 `/book/` 与 `/fr/book/` 以外的 public marketing landing 页面 SEO。
- 替换 mdBook，或引入新的外部 SEO 服务。

## Decisions

### Decision: 把 SEO 做成 repo 自己维护的 post-build injector
这次 SEO 变更横跨生成后的 book HTML、绝对 canonical URL、双语等价关系、JSON-LD，以及根目录级别的 sitemap / robots 产物。构建后脚本可以直接处理最终的 `public/book/**` 与 `public/fr/book/**`，而这些目录已经包含了 mdBook 输出和 repo 自己注入的 reader shell 改造。

考虑过的替代方案：
- 把全部 SEO 逻辑塞进 `theme/index.hbs`。否决，因为模板层并不天然掌握绝对站点 origin、精确的双语等价关系、根 sitemap 生成能力，以及跨两个 edition 的页面 description 提取结果。

### Decision: 使用 edition-local SEO override 数据，并对常规章节回退到自动 lede
大多数编号章节已经有可用的首段文字，可以直接作为唯一 description 的基础。像封面落地页、免责声明、图表/表格/公式索引、术语表、参考文献等特殊页面，则更适合使用人工整理的文案，因为它们的首个 block 往往过短、过于重复，或者不适合直接拿来做 SEO 描述。

因此设计上会把人工维护的 SEO overrides 放在 edition-local JSON 文件里，其余页面继续复用 `build_reader_page_meta.mjs` 现有的 lede 提取结果。这样只有真正需要人工控制的页面才需要手写 copy。

考虑过的替代方案：
- 把所有 metadata 直接硬编码进 injector 脚本。否决，因为这会把编辑层 copy 藏进实现逻辑里，后续维护成本更高。
- 要求每个页面都手写 description。否决，因为对本来就有合适正文首段的标准章节来说，这会引入不必要的维护噪音。

### Decision: 把跨语言导航映射和 SEO 等价映射拆开
现有导航映射会在没有译文时主动回退到目标语言首页。SEO 需要更严格的契约：只有真实等价页才发布 reciprocal `hreflang`；否则只保留 self-reference 与 `x-default`。

实现会把这套映射数据提取到一个共享模块中，并导出两种视图：
- 给 reader UI 使用的 navigation mapping
- 给 canonical alternates 和结构化数据 peer links 使用的 SEO equivalence mapping

考虑过的替代方案：
- 继续复用当前 UI map 来生成 `hreflang`。否决，因为这会继续发布非等价 alternate，正好违背了用户刚刚确认的策略。

### Decision: 让图书根路径停留在封面页，把进入正文的动作放到显式 CTA 上
`/book/` 与 `/fr/book/` 现在已经是 canonical 的落地页，承担 `Book` schema、侧边栏 `Cover` 激活态以及 canonical URL 的职责。因此它们应该稳定停留在封面页，而不是一进入就自动前送到默认阅读章节。封面上的 `Start reading` / `Commencer la lecture` CTA 已经提供了明确的“进入正文”入口，不需要再让图书根路径本身变成不稳定跳板。

考虑过的替代方案：
- 保留自动前送，只对侧边栏 `Cover` 做特殊处理。否决，因为这样会保留同一个用户问题：`Cover` 目的地最终还是落在一个“主要职责是离开封面”的路由上。

### Decision: 基于最终 canonical page inventory 生成 discovery artifacts
`book-sitemap.xml` 与 `robots.txt` 应该反映所有构建步骤完成后的真实可发布页面。生成器会遍历最终 public 下的 book 输出，排除 `chapters/front-matter.html` 这类纯跳转页，并统一输出 `https://upstreamatlas.com` 下的绝对 URL。

这个设计有意不把当前 mdBook `site-url` 当作 SEO 真值来源。英文 `book.toml` 仍然指向历史路径 `/west-africa-petroleum-book/book/`，因此 canonical URL 生成必须依赖 repo 自己维护的站点 origin 配置。

考虑过的替代方案：
- 直接从源 Markdown 或 `SUMMARY.md` 生成 sitemap。否决，因为那样会忽略构建后路由归一化和跳转页排除规则。

### Decision: 按页面类型输出 structured data，而不是所有页面统一套一个 schema
落地页输出 `Book` JSON-LD。编号章节页输出 `Chapter` 加 `BreadcrumbList`。像 glossary、bibliography、辅助索引这类参考页输出 `WebPage` 加 `BreadcrumbList`，让结构化数据与页面实际语义保持一致。

考虑过的替代方案：
- 对所有 `/chapters/*.html` 页面统一输出 `Article`。否决，因为 front matter 和 reference index 并不是 article，强行统一只会让 schema 更嘈杂，也不准确。

## Risks / Trade-offs

- [SEO override 文件可能和页面 inventory 漂移] → override 文件保持 edition-local，并对标准章节回退到自动 lede，同时增加测试，发现空 metadata 或重复 metadata 就直接失败。
- [语言等价关系变化会破坏 `hreflang`] → 把 SEO equivalence map 收敛到一个共享模块里，并用代表性的“等价页 / 非等价页”样本写测试。
- [构建后 HTML 重写可能伤到 reader 输出] → 重写范围只限于 `<head>` 与新增 discovery artifacts，同时增加回归检查，确认代表性章节正文仍在静态 HTML 中。
- [当前不同来源的书名不一致] → 对落地页和封面 metadata 使用人工 SEO override，而不是盲信当前 mdBook title 字符串。

## Migration Plan

1. 先补 OpenSpec 工件和失败的 metadata / sitemap 测试。
2. 引入共享 SEO helper 与 edition-local override 数据。
3. 为 `public/book/**` 和 `public/fr/book/**` 实现 post-build SEO injector。
4. 基于最终页面 inventory 实现 sitemap / robots 生成，并把两步接入 `scripts/build_site.mjs`。
5. 重建站点，运行定向 Python / site 校验，并检查代表性的英文和法文输出。
6. 如需回滚，从构建链中移除 SEO injector 与 sitemap / robots 步骤，恢复原有映射安排，然后重新构建站点。

## Open Questions

- None for this change. The only policy decision about untranslated English pages was resolved by the user: keep self-reference plus `x-default`, and do not emit a non-equivalent French alternate.
