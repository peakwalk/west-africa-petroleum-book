## Context

当前多语言拓扑虽然可用，但结构上并不一致：

- 英文内容、mdBook 配置以及生成后的 landing/legal/chapter 页面都位于仓库根目录。
- 法文内容则分散在 `src-fr/`、`books/fr/`、`fr/` 和 `public/fr/` 中。
- `config/editions.json` 中的 edition registry 逐项枚举了许多派生路径（`bookRoot`、`sourceRoot`、`summaryPath`、`chapterRoot`、`legalRoot`、`figureRoot`、`figureManifestPath`、`localeCatalog`），而不是声明一个 locale 根目录后统一推导。
- 根目录静态 HTML（`index.html`、`chapters/index.html`、legal 页面、`fr/*.html`）仍被版本控制，而构建最终又会重新发布到 `public/`。

这种结构把两种维度混在了一起：

1. 语言归属：哪些文件属于某个语言版本；
2. 构建阶段：哪些是源输入，哪些是最终发布产物。

这次变更属于跨模块的仓库重构。它会影响 Node 生成器、mdBook 入口、Python 校验脚本、preview 流程和测试断言。法文版变更已经建立的发布路由约束仍然有效：英文继续使用根路径，法文继续使用 `/fr/`。

## Goals / Non-Goals

**Goals:**
- 让每个语言版本都使用同样的内部工作区结构。
- 保持当前公开路由和语言切换行为不变。
- 将 edition 配置简化为“每个语言一个根目录 + route prefix + manuscript alias”。
- 让 `public/` 成为唯一的生成发布目录。
- 删除 `public/` 之外受版本控制的 landing/legal/chapter 生成 HTML。
- 让 locale-specific 的 figure manifest 与校验输入与新工作区根目录保持一致。

**Non-Goals:**
- 不改变 `/`、`/book/`、`/fr/`、`/fr/book/` 任一公开 URL。
- 不替换 mdBook，也不改掉当前共享 theme 模型。
- 不把英文与法文内容合并成一棵混合语言 Markdown 树。
- 不在本次变更中重写 figure 渲染算法，除非新目录结构要求同步调整路径和归属。
- 不为公共站点引入运行时 i18n 或客户端模板渲染。

## Decisions

### 1. 为每个语言版本引入单一 edition workspace 根目录

每个语言版本都会迁移到 `editions/<locale>/` 下，并使用固定的内部结构：

```text
editions/
  en/
    book.toml
    locale.json
    site/
      index-main.html
      legal/
    content/
      SUMMARY.md
      chapters/
      images/
        figure-manifest.json
  fr/
    book.toml
    locale.json
    site/
      index-main.html
      legal/
    content/
      SUMMARY.md
      chapters/
      images/
        figure-manifest.json
```

这样每个 edition 都有一个清晰的归属边界。凡是随语言变化而变化的文件，都必须位于对应 edition 根目录之下；共享资源、theme、脚本和 manuscript alias 继续保留在顶层共享区域。

备选方案：
- 保留 `src/` 与 `src-fr/` 的拆分，仅新增 `books/en` 和 `site/en`。否决，因为这仍会保留多套路径约定，并且继续把英文根目录作为结构特例。

### 2. 将 edition registry 收敛为 `editionRoot` 加路由信息

`config/editions.json` 将只声明：

- `locale`
- `editionRoot`
- `routePrefix`
- manuscript alias 路径
- 可选的 figure text replacement map

其余路径全部作为约定派生：

- `bookConfigPath = <editionRoot>/book.toml`
- `localeCatalogPath = <editionRoot>/locale.json`
- `siteRoot = <editionRoot>/site`
- `landingMainPath = <editionRoot>/site/index-main.html`
- `legalRoot = <editionRoot>/site/legal`
- `contentRoot = <editionRoot>/content`
- `summaryPath = <editionRoot>/content/SUMMARY.md`
- `chapterRoot = <editionRoot>/content/chapters`
- `figureRoot = <editionRoot>/content/images`
- `figureManifestPath = <editionRoot>/content/images/figure-manifest.json`

这能让 Node 与 Python 侧对同一语言版本使用完全一致的路径推导规则，也能减少 registry 漂移类问题。

备选方案：
- 继续在 registry 中显式保留每条派生路径，只调整文件位置。否决，因为重复维护路径目录本身就是当前维护成本的一部分。

### 3. 将 `public/` 视为唯一发布输出，并停止在其他地方版本控制静态 HTML

landing、legal 和 chapter-library 生成器将直接写入 `public/`，而不再先生成根目录 HTML，再由 `build:site` 二次复制。迁移后：

- `public/index.html`、`public/chapters/index.html` 和根 legal 页面直接由生成器产出。
- `public/fr/index.html`、`public/fr/chapters/index.html` 和法文 legal 页面直接由生成器产出。
- `public/book/` 与 `public/fr/book/` 继续由 mdBook 加 post-build reader 脚本产出。

仓库根目录和 `fr/` 将不再保存生成后的发布页面。

备选方案：
- 保留根目录和 `fr/` 页面，以便人工快速查看。否决，因为这会复制发布态产物、模糊源码归属，还会迫使测试维护“备份/恢复生成页”的复杂逻辑。

### 4. 让 route-prefix 语义独立于内部工作区布局

内部 edition workspace 会变得完全对称，但路由行为依然刻意保持不对称：

- 英文 `routePrefix = ""`
- 法文 `routePrefix = "fr"`

这样既能保留历史链接和当前 edition spec，也能让内部结构彻底规则化。

备选方案：
- 引入 `/en/` 与 `/en/book/`，与 `/fr/` 完全对称。否决，因为这会变成用户可见的路由迁移，并带来不必要的 SEO 与兼容成本。

### 5. 将根级 `build` 工作流切换为站点总装器，而不是旧的单语路径

`package.json` 目前保留了遗留命令，会在根目录生成页面和一个根级 `book/` 目录。迁移后的稳定工作流应为：

- `npm run build:site` 是唯一标准构建入口。
- `npm run build` 变成 `npm run build:site` 的别名。
- preview 与校验脚本统一把 `public/` 视为已装配好的站点产物根。

这样可以避免长期并存两套行为不一致的构建入口。

备选方案：
- 无限期保留旧构建流和新构建流。否决，因为双工作流会持续把旧路径假设重新引入测试和贡献者习惯中。

### 6. 采用“先兼容、再删除”的分阶段迁移策略

这次迁移会刻意拆成三个阶段：

1. 建立 `editions/` 并迁移内容；
2. 切换加载器和生成器；
3. 删除旧根目录与受版本控制的生成页面。

在最终清理前，这能保持回滚足够简单。

备选方案：
- 一次性搬迁所有文件并同步改掉所有脚本。否决，因为这会把 mdBook 路径解析、figure 校验和渲染测试全部绑进同一个高风险失败域。

## Risks / Trade-offs

- [移动 `book.toml` 后 mdBook 的 theme 或资源相对路径失效] → 同步调整两个 edition 的 `book.toml`，并为 `public/book/index.html` 与 `public/fr/book/index.html` 添加构建断言。
- [测试仍依赖根目录 HTML 或 `fr/` 内容] → 在删除旧生成页之前，先把渲染测试迁移到 `public/` 或临时输出目录。
- [Python 与 Node 对派生路径规则理解不一致] → 在 `scripts/shared/site-editions.mjs` 和 `scripts/edition_config.py` 中显式固化 `editionRoot` 派生契约，并增加 registry 结构测试。
- [迁移内容后 figure manifest 或 replacement map 路径失效] → 将 manifest 与 edition 内容根一起迁移，并保留 figure root 归属与 manifest 路径测试。
- [兼容窗口期间贡献者继续编辑旧目录] → 在仓库文档中声明新的 edition 根路径，并在新流水线稳定后尽快删除旧兼容层。
- [删除受控静态页面后人工预览不再“开箱即看”] → 统一用 `npm run build:site` 与 `scripts/preview.sh` 进行检查；接受这项权衡以换取源码/产物边界清晰。

## Migration Plan

1. 创建 `editions/en/` 与 `editions/fr/` 的目标目录结构，并把各语言自有输入复制进去；此时保留旧路径不删。
2. 重构 `config/editions.json`、`scripts/shared/site-editions.mjs` 和 `scripts/edition_config.py`，统一使用 `editionRoot` 与派生子路径。
3. 将 mdBook 配置迁移到 `editions/en/book.toml` 与 `editions/fr/book.toml`，并更新 `build_site.mjs`，使其分别构建到 `public/book` 和 `public/fr/book`。
4. 将 landing/legal/chapter-library 源输入迁移到 `editions/*/site/`，并更新生成器读取这些新位置。
5. 为生成器增加 output-root 支持，并修改站点装配器，让生成器直接写入 `public/`，不再先生成根目录受控页面。
6. 更新渲染测试、preview 脚本和 `package.json` 构建入口，使 `public/` 成为唯一发布产物。
7. 在 direct-to-`public/` 流程稳定并通过全部测试后，删除旧的生成 HTML（`index.html`、`chapters/index.html`、根 legal 页面、`fr/`）。
8. 在新 edition roots 成为唯一事实来源后，删除遗留源码路径与兼容层（`src/`、`src-fr/`、`books/fr/`、根 `book.toml`、旧 locale catalog 位置）。

回滚策略：

- 在第 7 步之前，回滚只需撤销 registry 与脚本切换，因为旧根目录仍然存在。
- 在第 7 步之后，回滚需要从 Git 恢复被删除的生成页面层，并回退 direct-to-`public/` 生成器变更。
- 在新的 build、parity 和 figure checks 一起通过之前，不删除旧源码目录。

## Open Questions

- 规划阶段没有遗留开放问题。目标结构、路由兼容约束，以及“只以 `public/` 作为输出”的模型都已固定。
