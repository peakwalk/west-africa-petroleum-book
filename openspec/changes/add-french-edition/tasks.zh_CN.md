## 1. Establish edition inputs and source topology

- [x] 1.1 在稳定的 `resources/editions/` 目录结构下增加英文与法文 DOCX/PDF 的 canonical alias paths，并在共享 edition registry 中记录它们。
- [x] 1.2 增加共享 edition registry 和各版本的 locale catalog，用于定义 route prefixes、source roots、manuscript aliases、figure roots 与本地化 UI labels。
- [x] 1.3 创建法文源树，保持与英文版一致的 chapter slugs、legal page keys 与 figure numbering，并补齐翻译后的 landing/legal/book 内容占位或最终文案。

## 2. Refactor public-page generation for localized editions

- [x] 2.1 让 `scripts/shared/landing-shell.mjs` 具备 locale-aware 能力，覆盖 links、navigation labels、CTA copy、footer copy、legal links，以及一个可见的 header-level 语言切换入口和对应版本目标。
- [x] 2.2 重构 `scripts/generate-index-page.mjs`、`scripts/generate-legal-pages.mjs` 和 `scripts/generate-chapters-page.mjs`，使其能从共享生成逻辑和 edition config 中渲染两个版本。
- [x] 2.3 为 landing 入口增加 neutral-entry 浏览器语言检测：英文保持默认，但当浏览器偏好法语且路由尚未显式指定版本时，跳转到 `/fr/`。
- [x] 2.4 更新站点输出装配逻辑，使 `public/`、`public/fr/`、`public/assets/` 和 `public/fr/assets/` 能稳定生成且互不覆盖。

## 3. Add French mdBook generation and reader-shell localization

- [x] 3.1 增加法文 mdBook 配置与源接线，使英文 book 继续位于 `/book/`，法文 book 构建到 `/fr/book/`。
- [x] 3.2 重构 reader 后处理步骤（`build:book-js`、`build:static-reader-sidebar`、`build:reader-meta` 以及任何新增的 localization step`），使其按版本运行，并注入本地化 shell 字符串与 header-level language-switch metadata。
- [x] 3.3 更新 `theme/index.hbs` 与 `theme/custom.js` 的集成点，使 toolbar labels、outline labels、search text、previous/next labels 以及一个可见的 book header 语言切换入口都能被注入本地化文案，而不必拆出两套漂移的 theme 目录。
- [x] 3.4 为 book 入口增加 neutral-entry 浏览器语言检测：英文保持默认，但当浏览器偏好法语且路由尚未显式指定版本时，跳转到 `/fr/book/`。

## 4. Make DOCX parity and figure validation edition-aware

- [x] 4.1 将 `scripts/docx_parity/*` 中英文专用的 chapter marker 假设替换为由 edition 数据驱动的 chapter-title 与 anchor 规则。
- [x] 4.2 让 `scripts/docx_figures/*`、`build_docx_figure_manifest.py` 和 `check_docx_figures.py` 都消费 edition-scoped 的 summary paths、chapter roots、figure roots、manuscript aliases 与可选 text-replacement maps。
- [x] 4.3 在 `package.json` 中新增英文与法文专用的 parity/figure 命令，并增加一个同时校验两个版本的顶层命令。
- [x] 4.4 用法文手稿派生的发布图片替换当前 bootstrap 的法文图片树，直到 `src-fr/images` 不再依赖英文来源的 figure 二进制文件。

## 5. Extend verification and release gates

- [x] 5.1 更新 `scripts/test-site-render.sh` 及相关源码/渲染断言，使其同时校验英文根路径输出与法文 `/fr/` 输出，包括本地化 shell 字符串和 language-switch links。
- [x] 5.2 更新所有默认只支持单版本的 Python 或 shell 测试，使其接受 edition config 并校验 locale-specific 输出。
- [x] 5.3 将双版本构建与校验流程纳入 `.github/workflows/pages.yml`，确保任一版本失败时 Pages 发布失败。
