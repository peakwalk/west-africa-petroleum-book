## Context

当前仓库在结构上是单版本的：

- `src/` 是 landing、legal、chapters 和 book assets 的唯一内容根目录。
- `book.toml` 只声明一个英文 mdBook 构建。
- landing 生成脚本和 `scripts/shared/landing-shell.mjs` 内嵌英文文案与英文路由。
- `theme/index.hbs` 与 `theme/custom.js` 内嵌英文 reader 标签，并默认只有一个版本。
- DOCX parity 与 figure inventory 脚本把 `Chapter N:` 之类的英文标记写死。

法文手稿输入已经存在于 `resources/` 中，但它们并不能直接接入当前栈：

- 法文 DOCX 不会暴露英文 chapter title，因此当前 parity extractor 只能把它识别成前言部分；
- 法文 PDF 文件名包含 Unicode 重音字符，在 shell 命令和 package script 中很容易处理出错；
- 当前 figure 与 manifest 流水线只有一个根目录 `src/images/figure-manifest.json`，并且部分逻辑是英文专用的；
- 当前法文源树把 `src-fr/images` 指向 `src/images`，因此法文 book 页面会直接消费与英文相同的已发布二进制图片，即便法文手稿与英文不同。

因此，这不是一个简单的文案复制任务，而是一次跨层发布架构变更。

## Goals / Non-Goals

**Goals:**
- 保持英文版在当前路由上稳定运行。
- 在 `/fr/` 与 `/fr/book/` 下新增法文版。
- 通过一套共享生成与校验栈复用两个版本。
- 保持 chapter slug、figure 编号和页面族在两个语言版本之间对齐，使语言切换具备确定性。
- 让 neutral entry routes 默认停留在英文版，同时在浏览器偏好法语时自动切换到法文版。
- 让 parity 与 figure validation 具备 edition-aware 能力，包括法文章节解析与法文手稿别名。

**Non-Goals:**
- 引入完整的运行时浏览器 i18n 或逐页客户端内容翻译。
- 从英文源动态翻译内容。
- 将英文与法文内容混入同一棵 Markdown 源树。
- 用新的框架重构站点或替换 mdBook。

## Decisions

### 1. 用共享 edition registry 配合并行 locale source roots

我们保留 locale-specific 的内容树：英文继续使用 `src/`，法文新增 `src-fr/`。一个受版本控制的共享 edition registry 统一声明每个版本的：

- locale code
- public route prefix
- source root
- legal content root
- figure root 与 manifest path
- manuscript alias paths
- mdBook config path
- locale string catalog path

这是最符合第一性原理与 MECE 的拆分：

- 内容差异放在 locale roots；
- 生成行为放在共享脚本；
- 发布编排放在顶层 build/test 命令。

备选方案：
- 引入运行时 i18n，仅保留一棵源树。拒绝原因是章节、legal 文案、figure caption 和 PDF-backed assets 都是版本级内容，不只是 UI 字符串。

### 2. 在两个版本之间保持完全一致的内部 slug 与 figure 编号

法文版将与英文版使用相同的内部 chapter 文件名和 figure 编号，即使页面标题和正文已经被翻译。这样可以保持：

- `theme/custom.js` 中的 page variant detection
- chapter-library 推导逻辑
- list-of-figures/list-of-tables 引用
- 对等页面间的语言切换

都保持简单且确定。

备选方案：
- 使用法文化文件名，再维护一张 slug 映射表。拒绝原因是这会把每个生成脚本、book 后处理脚本和语言切换规则都升级成双向映射系统，但没有足够的用户收益来抵消复杂度。

### 3. 为每个版本增加稳定的 ASCII 手稿别名路径

我们会引入诸如 `resources/editions/en/reference.docx` 和 `resources/editions/fr/reference.docx` 这类 canonical alias path，并为 PDF 提供对应别名。构建与校验命令将指向这些别名，而不是原始描述性文件名。

这样可以避免：

- shell quoting 漂移
- 组合重音与分解重音带来的 Unicode normalization 差异
- 在 `package.json` 和 Python 脚本中重复硬编码资源路径

备选方案：
- 在每条命令中继续直接使用原始资源文件名。拒绝原因是法文 PDF 名称本身已经存在 normalization 风险，而且项目即将进入多 locale 输入阶段。

### 4. 通过在每个 edition prefix 下镜像 shared assets 来保持相对路径稳定

当前 public pages 与 mdBook theme 大量依赖相对资源路径。对于 `/fr/book/...` 页面，现有相对路径模式天然会解析到 `/fr/assets/...`。与其整体改造成根相对 URL，不如直接把共享资源复制到：

- `public/assets`
- `public/fr/assets`

这样 landing pages 和 book pages 都能继续沿用当前路径模型，theme 的风险最小。

备选方案：
- 全站改用 root-relative asset URL。拒绝原因是当前 GitHub Pages 部署依赖相对路径行为；如果同时改 landing 和 mdBook 输出，风险会比复制静态资源更高。

### 5. 通过 locale catalog 与 post-build injection 本地化 reader-shell 文案

mdBook theme 在 `theme/index.hbs` 中包含用户可见标签，在 `theme/custom.js` 中包含依赖行为的字符串。我们会为每个版本引入 locale catalog，并让 book 的 post-build 流水线把 locale-specific 字符串和运行时配置注入已构建的 HTML/JS 表面。

这样无需维护两套分叉的 theme 目录，同时仍然可以支持：

- 翻译后的 toolbar 标签
- 翻译后的 search placeholder 与 empty-state 文案
- 翻译后的 outline 标签
- 翻译后的 previous/next 标签
- landing header 中可见的语言切换入口
- book header 中可见的语言切换入口

备选方案：
- 创建独立的 `theme` 与 `theme-fr` 目录。拒绝原因是 theme 文件绝大部分是共享的，复制后会快速漂移。

### 6. 仅在 neutral entry routes 上使用受限的客户端 locale 协商

由于 GitHub Pages 是静态托管，站点无法在服务端读取 `Accept-Language` 并在返回 HTML 前完成语言协商。更稳妥的做法是：

- neutral entry routes 仍以英文内容作为默认渲染结果；
- 仅在 neutral entry routes 上运行一个很小的客户端语言检测；
- 当 `navigator.languages` 或 `navigator.language` 表明偏好法语时，跳转到 `/fr/` 或 `/fr/book/`；
- 对 `/fr/...` 这类显式版本路由绝不做自动覆盖；
- 一旦读者通过语言切换显式选择了版本，就让显式路由优先于浏览器偏好。

这样可以在满足需求的同时，把逻辑限制在可预测的入口层，而不是升级成完整的客户端 i18n。

备选方案：
- 服务端 locale 协商。拒绝原因是当前部署目标是静态托管。
- 对所有页面都按浏览器语言自动跳转。拒绝原因是显式路由选择必须优先，章节和 legal 深链接也必须保持稳定。

### 7. 通过共享 JSON 输入让 Python 校验配置具备 edition-aware 能力

Node 构建脚本与 Python 校验脚本都需要读取同一份 edition metadata。因此 registry 应存为两端都能直接消费的格式，Python 专用的 regex 与 anchor metadata 也应被表达成数据，而不是继续以硬编码常量存在。

这些 metadata 将包括：

- chapter-title patterns
- front/back matter title patterns
- per-edition docx/pdf alias paths
- figure replacement map path（如果需要）

备选方案：
- 保留一份 JS 配置，再在 Python 里手写一份等价配置。拒绝原因是 duplicated locale metadata 很容易漂移，并导致 parity/figure 校验静默失真。

### 8. 用真实的法文 figure root 承接隔离阶段，再逐步用法文手稿重渲染覆盖

法文版需要分成两个清晰阶段：

- **隔离阶段**：用真实的 `src-fr/images/` 目录替换 `src-fr/images -> ../src/images` 软链，使法文构建和 manifest 可以独立演进；
- **内容收敛阶段**：按 figure kind 从法文 DOCX/PDF 输入重渲染法文发布图片，直到法语 web 资源在内容和布局上与法语手稿一致。

在隔离阶段，可以先用当前已发布图片集引导生成 `src-fr/images/`，以保持构建路径稳定。但这只是中间态，不是发布终态。发布终态必须是完整的法文手稿派生图片树。

这样拆分是必要的，因为：

- 构建独立性和内容保真是两个不同问题；
- 如果法文图片树仍然是英文根目录的软链，就无法对法文 manifest 做独立校验，也无法逐步修复法文图片；
- 部分图片必须依赖 PDF-backed 渲染才能保证版式一致，另一些则可以走 DOCX-native 提取。

备选方案：
- 在所有法文图片全部重渲染完成前，继续保留法文图片根目录软链。拒绝原因是这会阻断 edition-scoped manifest，也会掩盖法文页面是否还在依赖英文二进制图片。

## Risks / Trade-offs

- [French source topology diverges from English slug topology] -> 强制法文源树复用同一套 slug 与 figure numbering，并为语言切换目标增加 render assertion。
- [Post-build localization misses new reader strings] -> 统一通过 locale catalog 注入，并在 `public/fr/book` 上增加法文 shell 字符串断言。
- [Duplicated static assets increase publish size] -> 当前接受适度复制以换取路径稳定；等双版本稳定后再评估去重。
- [DOCX extraction rules remain too English-centric] -> 将章节与锚点规则迁移到 edition data，并在接入发布 gate 前补上法文章节 marker 的 fixture 覆盖。
- [Figure assets drift between editions] -> 保持 locale-scoped 的 figure roots 和 manifests，尽早落地真实的法文图片目录，并要求发布前完成法文手稿重渲染与 edition-scoped figure validation。
- [Bootstrap 拷贝被误当成最终法文图片] -> 明确把复制图片只当成隔离阶段的中间态，并保留一个显式任务把它们替换成法文手稿派生图片。

## Migration Plan

1. 先引入 canonical manuscript aliases 与 edition registry，不改公开路由。
2. 增加法文源树，保持 slug 镜像，同时补入法文 legal 内容和法文 landing 文案。
3. 重构 landing/legal/chapters 生成脚本与 shared shell links，使其能读取 edition data 并写出 `/fr/*`。
4. 增加法文 mdBook 配置，并扩展 book 后处理脚本，让 `/fr/book` 能正确本地化，并提供 header-level 语言切换。
5. 让 parity 与 figure validation 具备 edition-aware 能力，完成法文图片根目录隔离，并新增法文专用命令。
6. 按法文手稿重渲染法文发布图片，直到法文图片树不再依赖英文派生二进制文件。
7. 将顶层 build/test/Pages 工作流提升为双版本强校验。

回滚策略：

- 在 edition registry 和顶层构建编排中禁用法文版入口；
- 保持英文根路径构建不变，因为它的路由和内容根目录都不会迁移。

## Open Questions

- 规划层面无待决问题。本变更默认假设法文与英文章节 slug 保持一致，并将法文版作为 `/fr/` 下的同级路由族发布。
