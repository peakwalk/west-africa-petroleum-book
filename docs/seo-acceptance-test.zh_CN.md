# `https://upstreamatlas.com/` SEO 验收测试

## 目标

这份清单用于验证 SEO 变更不是“代码已经上线”而已，而是真的以 Google 能理解的方式生效，能够影响抓取、索引和搜索展示。

对这个项目来说，“SEO 已起作用”分成 4 件事：

1. 公开页面返回了正确的 HTML、metadata、canonical 和语言信号。
2. Google 能抓取并渲染 live 页面。
3. Google 已索引我们期望被索引的 canonical URL。
4. Search Console 在部署后开始出现发现、索引或搜索活动数据。

不要把 `site:upstreamatlas.com` 当成唯一验收标准。它只能算粗略 smoke check，不是权威结论。

## 范围

至少对以下 URL 运行测试：

- 站点根首页：`https://upstreamatlas.com/`
- 英文 book 落地页：`https://upstreamatlas.com/book/`
- 法文 book 落地页：`https://upstreamatlas.com/fr/book/`
- 代表性的英文深页章节：
  `https://upstreamatlas.com/book/chapters/chapter-05-hydrocarbon-value-chain.html`
- 代表性的法文深页章节：
  `https://upstreamatlas.com/fr/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html`

如果本次发布还改了其他 canonical book 页面，每种页面类型至少再补一个变更 URL。

## 前置条件

- 生产部署已经完成。
- 你有可用的终端和 `curl`。
- 你有 `upstreamatlas.com` 域名属性的 Google Search Console 权限。
- 你知道本次生产发布时间。

## 通过标准

最终验收结果按下面判定：

- `PASS`：技术检查通过，Google live test 通过，索引结果健康，Search Console 已出现预期抓取、索引、搜索信号。
- `PARTIAL PASS`：技术检查通过，但 Google 侧索引证据还在等待。
- `FAIL`：公开 HTML 错误、canonical 或 hreflang 错误、页面被阻止抓取，或 Google 报错把页面判成了错误 canonical / 不可索引。

## 测试用例

### SEO-AT-001 公网可访问性和 HTTP 状态

目的：
确认 URL 公开可访问，没有坏状态码或重定向循环。

步骤：

1. 运行：

   ```bash
   curl -I https://upstreamatlas.com/
   curl -I https://upstreamatlas.com/book/
   curl -I https://upstreamatlas.com/fr/book/
   curl -I https://upstreamatlas.com/book/chapters/chapter-05-hydrocarbon-value-chain.html
   curl -I https://upstreamatlas.com/fr/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html
   ```

2. 如果任何 URL 返回 `301` 或 `302`，用 `-L` 重新跑并记录最终目标：

   ```bash
   curl -sIL https://upstreamatlas.com/book/
   ```

预期结果：

- canonical 目标 URL 返回 `200 OK`。
- 没有重定向循环。
- 深页章节 URL 不会跳到无关页面。

需要保存的证据：

- 5 个 URL 的终端输出

### SEO-AT-002 robots.txt 和 sitemap 暴露

目的：
确认 Google 能发现 sitemap，并且 sitemap 中列的是 canonical URL。

步骤：

1. 获取 `robots.txt`：

   ```bash
   curl -sL https://upstreamatlas.com/robots.txt
   ```

2. 确认其中包含：

   ```text
   Sitemap: https://upstreamatlas.com/book-sitemap.xml
   ```

3. 获取 sitemap：

   ```bash
   curl -sL https://upstreamatlas.com/book-sitemap.xml
   ```

4. 确认它包含：

   - `https://upstreamatlas.com/book/`
   - `https://upstreamatlas.com/fr/book/`
   - 代表性的 EN/FR 深页章节 URL

5. 确认它不包含 redirect shim 页面，例如：

   - `https://upstreamatlas.com/book/chapters/cover.html`
   - `https://upstreamatlas.com/book/chapters/front-matter.html`
   - `https://upstreamatlas.com/fr/book/chapters/cover.html`
   - `https://upstreamatlas.com/fr/book/chapters/front-matter.html`

预期结果：

- `robots.txt` 可公开访问，并引用了 book sitemap。
- sitemap 使用的是完整绝对 URL。
- 只有应该进入搜索的 canonical URL 被列入。

需要保存的证据：

- `robots.txt` 输出
- `book-sitemap.xml` 输出

### SEO-AT-003 Title、description、canonical、robots 指令

目的：
确认关键 metadata 已经存在于 crawler 能拿到的 live HTML 里。

步骤：

1. 抓取各页面 HTML：

   ```bash
   curl -sL https://upstreamatlas.com/book/ > /tmp/book-en.html
   curl -sL https://upstreamatlas.com/fr/book/ > /tmp/book-fr.html
   curl -sL https://upstreamatlas.com/book/chapters/chapter-05-hydrocarbon-value-chain.html > /tmp/chapter-en.html
   curl -sL https://upstreamatlas.com/fr/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html > /tmp/chapter-fr.html
   ```

2. 检查 head 中的标签：

   ```bash
   rg -n "<title>|meta name=\"description\"|rel=\"canonical\"|name=\"robots\"" /tmp/book-en.html /tmp/book-fr.html /tmp/chapter-en.html /tmp/chapter-fr.html
   ```

3. 对每个页面确认：

   - 有且只有一个非空 `<title>`
   - 有且只有一个非空 `<meta name="description">`
   - 有一个绝对地址的 `<link rel="canonical">`
   - 没有误加 `noindex`

预期结果：

- metadata 存在于服务端返回的 HTML 中。
- canonical URL 是绝对生产地址。
- 没有 canonical 页面被 `noindex`。

需要保存的证据：

- 每页抽取出的标签输出

### SEO-AT-004 hreflang 双向关系和 x-default

目的：
确认等价语言页面互相引用正确。

步骤：

1. 抽取 alternate links：

   ```bash
   rg -n 'rel="alternate".*hreflang=' /tmp/book-en.html /tmp/book-fr.html /tmp/chapter-en.html /tmp/chapter-fr.html
   ```

2. 验证 `/book/` 和 `/fr/book/` 都包含：

   - 指向自己的 `hreflang`
   - EN/FR 双向 alternate
   - `x-default`

3. 验证代表性的 EN/FR 章节对都包含：

   - 指向自己的 `hreflang`
   - EN/FR 双向 alternate
   - `x-default`

4. 对任何没有真实翻译对应页的页面，验证：

   - 有指向自己的 `hreflang`
   - 有 `x-default`
   - 没有错误地指向非等价 URL

预期结果：

- 等价页面是双向互指的。
- alternate URL 都是完整绝对地址。
- 需要 fallback 的页面存在 `x-default`。

需要保存的证据：

- 每个测试页的 hreflang 抽取结果

### SEO-AT-005 结构化数据存在且与页面内容一致

目的：
确认 structured data 存在，而且描述的是页面上可见的内容，而不是与页面无关的隐藏内容。

步骤：

1. 抽取 JSON-LD：

   ```bash
   rg -n "application/ld\\+json|@type|\"url\"|\"name\"|\"inLanguage\"" /tmp/book-en.html /tmp/book-fr.html /tmp/chapter-en.html /tmp/chapter-fr.html
   ```

2. 验证：

   - `/book/` 和 `/fr/book/` 暴露 `Book` JSON-LD
   - 编号章节页暴露 `Chapter` 和 `BreadcrumbList`
   - schema 中的 `url` 与 canonical URL 一致
   - schema 语言与页面可见语言一致

预期结果：

- JSON-LD 存在于页面 HTML 中。
- schema 类型与页面类型匹配，并与可见内容一致。

需要保存的证据：

- 抽取出的 JSON-LD 片段

### SEO-AT-006 原始 HTML 中存在可抓取正文

目的：
确认重要正文在原始 HTML 中可见，而不是只能靠前端 JavaScript 才出现。

步骤：

1. 检查代表性章节页的原始 HTML：

   ```bash
   rg -n "<h1|Hydrocarbon Value Chain|value chain comprises three principal segments" /tmp/chapter-en.html
   rg -n "<h1|chaîne de valeur|secteur pétrolier" /tmp/chapter-fr.html
   ```

2. 用浏览器打开相同 URL，确认页面可见内容与原始 HTML 基本一致。

预期结果：

- 原始 HTML 中能找到章节 H1。
- 原始 HTML 中能找到至少一段代表性的正文。
- 浏览器渲染结果与原始 HTML 在 SEO 关键内容上基本一致。

需要保存的证据：

- 终端输出，证明 H1/正文存在于原始 HTML
- 浏览器截图

### SEO-AT-007 Search Console URL Inspection：Indexed result

目的：
确认 Google 当前索引里对这个 URL 的认知。这比单纯 HTTP 检查更有说服力。

步骤：

1. 打开 `upstreamatlas.com` 的 Search Console 属性。
2. 逐个检查以下 URL：

   - `https://upstreamatlas.com/`
   - `https://upstreamatlas.com/book/`
   - `https://upstreamatlas.com/fr/book/`
   - 代表性的英文深页章节
   - 代表性的法文深页章节

3. 对每个 URL 记录：

   - 状态是否以 `URL is on Google` 开头
   - user-declared canonical
   - Google-selected canonical
   - crawling 是否 allowed
   - indexing 是否 allowed
   - 是否出现在已提交 sitemap 中

预期结果：

- canonical 页面可索引。
- user-declared canonical 与 Google-selected canonical 一致；如果不一致，必须能解释并被接受。
- canonical URL 能关联到已提交的 sitemap。

需要保存的证据：

- 每个 URL 的 indexed result 截图

### SEO-AT-008 Search Console URL Inspection：Live test

目的：
确认 Google 现在就能抓取并渲染 live 页面。仅仅“页面上线可访问”并不能证明 Google 真能拿到它。

步骤：

1. 对相同 URL 点击 `Test live URL`。
2. 等待 live test 完成。
3. 记录：

   - live verdict
   - crawl allowed?
   - page fetch
   - indexing allowed?
   - 是否能看到 screenshot

4. 打开 `View tested page`，保存：

   - screenshot
   - raw HTML
   - HTTP response headers
   - page resources

5. 在返回的 HTML 中确认 title、canonical、hreflang 和代表性正文都存在。

预期结果：

- Live test verdict 为 `URL is available to Google`，或者是已知且不阻塞的 `URL is available to Google, but has issues`。
- Google 能抓取页面并产出 screenshot。
- Google 看到的 raw HTML 与公网 HTML 检查中的 SEO 关键内容一致。

需要保存的证据：

- live test verdict 截图
- Search Console 渲染截图
- `View tested page` 导出的 raw HTML

### SEO-AT-009 Search Console sitemap 提交

目的：
确认 Google 已经看到 sitemap，并且正在正常处理。

步骤：

1. 打开 Search Console > Sitemaps。
2. 如果还没提交，提交 `https://upstreamatlas.com/book-sitemap.xml`。
3. 记录：

   - 提交时间
   - fetch status
   - discovered URLs 数量
   - last read 时间

预期结果：

- Sitemap 提交成功。
- Search Console 能正常抓取 sitemap。
- 没有解析错误或访问错误。

需要保存的证据：

- sitemap 详情页截图

### SEO-AT-010 Search Console Page indexing 健康度

目的：
发现“技术上可访问，但仍然没被正确索引”的问题。

步骤：

1. 打开 Search Console > Page indexing。
2. 过滤 URL 范围：

   - `/book/`
   - `/fr/book/`

3. 检查代表性页面是否落在以下 excluded 状态：

   - `Discovered - currently not indexed`
   - `Crawled - currently not indexed`
   - `Duplicate, Google chose different canonical than user`
   - `Alternate page with proper canonical tag`

4. 对任何处于 excluded 状态的代表性 URL，继续点进去做 URL Inspection。

预期结果：

- canonical 目标页不会无故卡在 excluded 状态。
- 被排除的页面只应是有意排除的页面，例如 redirect shim 或非 canonical duplicate。

需要保存的证据：

- Page indexing 总览截图
- 对 excluded URL 的备注

### SEO-AT-011 部署后的搜索表现趋势

目的：
验证技术 SEO 变更开始对“发现或搜索活动”产生影响。这一项检查的是效果，不只是实现是否正确。

步骤：

1. 至少等一个完整抓取/索引周期。实际建议在以下时间点回看：

   - T+3 天
   - T+7 天
   - T+28 天

2. 打开 Search Console > Performance > Search results。
3. 应用过滤：

   - Page contains `/book/` 用于英文
   - Page contains `/fr/book/` 用于法文

4. 对比发布前后窗口的数据：

   - impressions
   - clicks
   - average position
   - indexed page coverage 趋势

5. 记录 book 落地页和代表性深页章节的变化。

预期结果：

- canonical book 页面在被索引后，impressions 不为 0。
- 发布后不会出现持续性的 indexed pages 或 impressions 崩塌。
- 如果整体流量较小，先出现 discovery / impressions，再出现 clicks，也算早期正向证据。

需要保存的证据：

- Search Console performance 导出的 CSV
- 发布前后截图

## 判定规则

写最终验收结论时，按下面规则判定：

- 如果 SEO-AT-001 到 SEO-AT-006 失败，说明发布还不具备 SEO 上线条件。
- 如果 SEO-AT-001 到 SEO-AT-006 通过，但 SEO-AT-007 到 SEO-AT-010 还没完成，结论应写成“技术实现正确，但还没完成完整 SEO 验收”。
- 如果 SEO-AT-001 到 SEO-AT-010 全部通过，SEO 实现可以验收通过。
- SEO-AT-011 是发布后的效果追踪项。它应该被持续跟踪，但不应在技术和索引检查已通过的情况下阻塞上线。

## 快速交接清单

这部分用于把最后的 Google 侧验证交接给有 Search Console 权限的人，避免对方还要通读整份长文档。

### 交接输入

- Property：`upstreamatlas.com`
- 发布时间：填写本次生产发布时间
- 需要检查的 URL：
  - `https://upstreamatlas.com/book/`
  - `https://upstreamatlas.com/book/chapters/chapter-05-hydrocarbon-value-chain.html`
  - `https://upstreamatlas.com/fr/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html`
- 需要提交或确认的 sitemap：
  - `https://upstreamatlas.com/book-sitemap.xml`

### 5 分钟 Search Console 清单

1. 打开 Search Console，提交或确认 `https://upstreamatlas.com/book-sitemap.xml`。
2. 对上面 3 个 URL 运行 URL Inspection，并记录 indexed result：
   - `URL is on Google` 或当前状态
   - user-declared canonical
   - Google-selected canonical
   - 是否 found in sitemap
3. 对同样 3 个 URL 运行 `Test live URL`，并保存：
   - live verdict
   - screenshot
   - tested HTML
4. 打开 Page indexing，检查代表性 URL 是否卡在以下状态：
   - `Discovered - currently not indexed`
   - `Crawled - currently not indexed`
   - `Duplicate, Google chose different canonical than user`
5. 在 T+7 和 T+28 打开 Performance > Search results，对比 `/book/` 和 `/fr/book/` 的发布后 impressions。

### Jira 证据模板

Search Console 检查完成后，把下面这段直接贴到 Jira：

```md
Search Console follow-up completed on YYYY-MM-DD.

Sitemap
- `https://upstreamatlas.com/book-sitemap.xml`
- Status:
- Last read:
- Any parse/fetch issues:

URL Inspection
- `/book/`
  - Indexed result:
  - User canonical:
  - Google canonical:
  - Found in sitemap:
- EN representative chapter
  - URL: `https://upstreamatlas.com/book/chapters/chapter-05-hydrocarbon-value-chain.html`
  - Indexed result:
  - User canonical:
  - Google canonical:
  - Found in sitemap:
- FR representative chapter
  - URL: `https://upstreamatlas.com/fr/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html`
  - Indexed result:
  - User canonical:
  - Google canonical:
  - Found in sitemap:

Live Test
- `/book/`:
- EN representative chapter:
- FR representative chapter:

Page Indexing Notes
- Any exclusion state observed:
- Any canonical mismatch observed:

Performance Follow-up
- T+7 impressions trend:
- T+28 impressions trend:

Final Verdict
- PASS / PARTIAL PASS / FAIL
- Notes:
```

## 备注

- Live test 通过不等于一定会被索引。Google 明确说过，live URL test 只能证明 Google 能访问这个页面用于索引，不能保证最终一定进入索引。
- 对多语言页面，Google 建议显式声明 alternate mapping，并要求每个语言版本列出自己和其他版本。`hreflang` 的用途是表达等价关系，不是强制 Google 用它判断页面语言。
- Structured data 有价值，因为它能帮助 Google 理解页面，但它必须描述该页面上可见的内容。

## 参考链接

- Google Search Central: [Tell Google about localized versions of your page](https://developers.google.com/search/docs/specialty/international/localized-versions)
- Google Search Central: [Introduction to structured data markup](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data)
- Google Search Central: [Build and submit a sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- Search Console Help: [URL Inspection tool](https://support.google.com/webmasters/answer/9012289?hl=en)
