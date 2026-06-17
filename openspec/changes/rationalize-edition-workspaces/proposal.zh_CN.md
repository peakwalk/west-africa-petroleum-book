## Why

当前仓库的多语言目录同时混杂了“语言归属”和“构建阶段”两种维度。英文源码和生成后的静态页面位于仓库根目录，而法文等价物又分散在 `src-fr/`、`books/fr/`、`fr/` 和 `public/fr/` 中。这种不对称结构让日常修改更容易出错，也让人难以判断哪些目录是源码、哪些目录是生成产物，并且会显著提高后续新增语言版本的成本。

法文版上线已经解决了路由与内容需求，但它保留了英文根目录特例，也让 `public/` 之外继续存在受版本控制的静态页面。下一步应当先把仓库整理成以 edition 为中心的统一源码模型，再继续叠加更多语言、资源和测试。

## What Changes

- 引入统一的 `editions/<locale>/` 工作区结构，用于承载各语言版本自己的 mdBook 配置、landing/legal 源内容、Markdown 正文、图像资源和 locale catalog。
- 在保持当前公开路由不变的前提下，将英文和法文输入迁移到对称的 `editions/en/` 与 `editions/fr/` 根目录中：英文仍发布到 `/` 与 `/book/`，法文仍发布到 `/fr/` 与 `/fr/book/`。
- 重构共享 edition 配置模型，让构建与校验脚本从 `editionRoot` 推导各语言路径，而不再分别维护 `sourceRoot`、`legalRoot`、`bookRoot`、locale catalog 等独立字段。
- 调整 landing、legal 和 chapter-library 生成器，使其直接写入 `public/`，而不是先在仓库根目录和 `fr/` 下生成受版本控制的 HTML。
- 在直接输出到 `public/` 的流水线稳定后，删除仓库根目录和 `fr/` 下受版本控制的静态 landing/legal/chapter 页面。
- 移除仅用于兼容旧拓扑的接线层，包括 `books/fr` 的符号链接 wiring 和根目录英文 `book.toml` 特例。
- 继续将共享资源、theme、校验脚本和 manuscript alias 保持在 edition 工作区之外，除非它们天然是语言专属的。

## Capabilities

### New Capabilities
- `edition-workspace-layout`：每个语言版本自己的站点、book 和 figure 输入都组织在一个对称的 edition 工作区根目录下。
- `edition-static-output-pipeline`：共享生成器与 mdBook 构建直接将双语输出发布到 `public/`，并且 `public/` 之外不再保留受版本控制的静态 HTML。

### Modified Capabilities
- None.

## Impact

- 受影响代码将包括 `config/editions.json`、`scripts/shared/site-editions.mjs`、`scripts/edition_config.py`、`scripts/build_site.mjs`、`scripts/generate-*.mjs`、`package.json`、preview 脚本和站点渲染测试。
- 各语言自有输入文件将从 `src/`、`src-fr/`、`book.toml`、`books/fr/`、`config/locales/` 以及根目录生成 HTML 迁移到 `editions/en/` 与 `editions/fr/`。
- 构建校验将从检查“根目录受控页面 + `public/` 产物”的混合模型，转为只把 `public/` 视为发布产物。
- 本次变更不会引入新的公开路由；它是一次内部目录拓扑与构建流水线重组，同时保持 URL 层兼容。
