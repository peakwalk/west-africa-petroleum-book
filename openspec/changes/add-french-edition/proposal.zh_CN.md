## Why

当前仓库只会从一套写死的英文源路径、英文标签和英文校验命令生成一个英文 landing page 和一个英文 mdBook。法文 DOCX 与 PDF 已经存在于 `resources/` 下，但现有流水线既不能把它们接入校验、构建与发布，也无法在不破坏英文版本的前提下增加法文版本；如果继续沿用现状，只能复制整套生成脚本。此外，当前法文源树还复用共享的英文图片根目录，这会让法语 web 页中的图在文字和布局上偏离法语 DOCX/PDF。

## What Changes

- 引入 edition-aware 发布模型：保留英文版在当前根路径，同时在 `/fr/` 与 `/fr/book/` 下新增法文版。
- 在 landing page header 和 book reader header 中增加可见的语言切换入口，使读者能从主导航表面直接在英文与法文之间切换。
- 增加 edition-neutral 入口行为：默认显示英文版，但当浏览器语言偏好为法语时，自动跳转到法文版。
- 增加一个统一的 edition registry，定义每个版本的源目录、手稿别名路径、输出前缀、book 配置、图像资源、locale 文案和校验输入。
- 重构 landing、legal、chapters 和 book 的后处理脚本，使其能从共享生成逻辑中渲染任一版本，而不是继续把英文路径与文案写死。
- 新增法文源树、法文 legal 内容、法文 landing 文案、法文 figure/manuscript 资源，并保持与英文版相同的 chapter/file slug 拓扑。
- 用真实的 locale-owned 法文 figure root 替换法文图片软链，使法文构建、manifest 和校验不再依赖英文共享图片目录。
- 扩展 DOCX parity 与 figure validation 流水线，使其能解析法文章节标记，并针对法文手稿与 PDF 输入执行图表校验。
- 按法文 DOCX/PDF 输入重渲染法文发布图片，直到法语 web 版不再把英文派生图片当作占位资源。
- 更新 build、test 与 Pages 发布命令，使两个版本一起生成、一起校验。

## Capabilities

### New Capabilities
- `localized-site-editions`：发布独立的英文与法文公开路由，并提供本地化的 landing、legal、chapter library 与 reader 入口。
- `localized-book-sources`：通过单一共享的 edition registry 解析每个版本的 Markdown、legal 内容、figure 资源和手稿输入。
- `localized-parity-validation`：让每个版本都能针对自己的 DOCX/PDF 源执行校验，包括法文章节解析与图表检查。

### Modified Capabilities
- None.

## Impact

- 受影响的源码会包括 `package.json`、`book.toml`/`book.fr.toml`、`theme/index.hbs`、`theme/custom.js`、`scripts/generate-*.mjs`、`scripts/build_*`、`scripts/check_docx_*` 和 `scripts/docx_figures/*`。
- 会新增法文 edition 内容与资源目录，以及 locale-specific 的手稿别名路径。
- `public/` 下的构建产物会扩展为 `/fr`、`/fr/assets`、`/fr/chapters` 和 `/fr/book`。
- GitHub Pages 构建和本地站点验证将从单版本生成升级为双版本生成。
