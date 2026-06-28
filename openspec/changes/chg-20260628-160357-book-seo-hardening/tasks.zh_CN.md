## 1. OpenSpec and failing SEO coverage

- [x] 1.1 补齐 proposal、design 和 `book-seo-indexability` capability spec，覆盖双语 book SEO hardening。
- [x] 1.2 先补失败测试，覆盖 sitemap / robots 生成、绝对 canonical metadata、reciprocal-vs-self-only `hreflang`、structured data，以及代表性英文/法文章节页的静态正文保留。

## 2. Book SEO metadata pipeline

- [x] 2.1 增加共享 SEO helper / config，覆盖站点 origin、canonical URL 构造，以及“导航映射”和“SEO 映射”的拆分。
- [x] 2.2 为落地页、章节页和参考页实现 post-build SEO injector，输出唯一 title / description / canonical、`hreflang`、`x-default` 和按页面类型区分的 JSON-LD。

## 3. Discovery artifacts and build wiring

- [x] 3.1 基于最终 canonical 的双语 book page inventory 生成 `book-sitemap.xml` 和根目录 `robots.txt`，并排除跳转页。
- [x] 3.2 在现有 reader metadata 和本地化步骤之后，把 SEO injector 与 discovery artifact 生成接入 `scripts/build_site.mjs`。

## 4. Verification and regression tightening

- [x] 4.1 更新 site-render 断言和 metadata 测试，让双语 book 输出一旦出现空 SEO 字段或重复 metadata 就直接失败。
- [x] 4.2 运行最小但足够的 build / test 命令，并检查代表性的英文和法文生成页，确认 SEO head markup 与 sitemap 输出符合预期。
- [x] 4.3 通过移除“图书首页自动前送到默认章节”的逻辑，让 `/book/` 和 `/fr/book/` 停留在封面页，同时保留显式阅读 CTA 和 locale 偏好跳转。
