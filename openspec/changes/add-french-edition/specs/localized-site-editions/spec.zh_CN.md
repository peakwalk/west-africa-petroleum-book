## ADDED Requirements

### Requirement: Edition-specific public routes
站点 MUST 在当前根路径发布英文版，并且 MUST 在 `/fr/` 下发布法文版。法文版 MUST 包含本地化的首页、legal、chapter library 和 book 路由，且不得覆盖英文版输出。

#### Scenario: Dual public roots are generated
- **WHEN** 站点构建成功完成
- **THEN** 输出目录同时包含 `public/index.html`、`public/book/index.html`、`public/fr/index.html` 和 `public/fr/book/index.html`

#### Scenario: French build does not replace English output
- **WHEN** 法文版在英文版之后生成
- **THEN** 已有英文根路径文件仍然存在，且英文路由前缀保持不变

### Requirement: Browser-language edition auto-selection on neutral entry routes
对于 edition-neutral 的入口路由，站点 MUST 在浏览器语言偏好不是法语时默认停留在英文版，并且 MUST 在浏览器偏好法语时自动跳转到对应的法文入口路由。这种语言协商 MUST 仅限于 neutral entry routes，MUST NOT 强制改写显式版本路由。

#### Scenario: Neutral landing entry defaults to English
- **WHEN** 读者打开 neutral landing 入口路由，且浏览器语言偏好不是法语
- **THEN** 英文 landing page 保持可见

#### Scenario: Neutral landing entry redirects French browsers
- **WHEN** 读者打开 neutral landing 入口路由，且浏览器语言偏好表明法语
- **THEN** 页面会在读者开始站内导航前跳转到法文 landing 路由

#### Scenario: Neutral book entry redirects French browsers
- **WHEN** 读者打开 neutral book 入口路由，且浏览器语言偏好表明法语
- **THEN** 页面跳转到法文 book 入口路由，而不是停留在英文 book 入口路由

#### Scenario: Explicit edition routes are respected
- **WHEN** 读者直接打开 `/fr/...` 或通过语言切换明确选择了英文路由
- **THEN** 站点不会仅因浏览器偏好另一种语言就覆盖这次显式路由选择

### Requirement: Localized public copy and navigation labels
每个版本 MUST 渲染自己的公开可见文案，包括 header、footer、legal navigation、chapter-library UI 和 book-reader shell。布局结构可以保持一致，但用户可见文案 MUST 与版本 locale 一致。

#### Scenario: Landing shell labels follow the edition locale
- **WHEN** 读者分别打开英文和法文 landing page
- **THEN** 根路径版本的导航标签、CTA 标签、footer 标题和 legal 标题使用英文，而 `/fr/` 版本使用法文

#### Scenario: Reader shell labels follow the edition locale
- **WHEN** 读者打开 `/book/` 和 `/fr/book/`
- **THEN** toolbar 标签、搜索占位文案、outline 标题和 chapter-pagination 标签按各自版本本地化

### Requirement: Cross-edition language switching
凡是在两个版本中都存在的公开页面族 MUST 提供语言切换入口，使读者能在英文与法文对等页面之间切换。只要两个版本都存在同名 slug，对等页面 MUST 保持同一内容目标。

#### Scenario: Landing header exposes the language switch
- **WHEN** 读者打开英文或法文 landing page
- **THEN** 页面 header 渲染一个可见的语言切换控件，并指向另一语言版本中的对等 landing page

#### Scenario: Book header exposes the language switch
- **WHEN** 读者打开英文或法文 book reader
- **THEN** 粘性 book header 渲染一个可见的语言切换控件，并指向另一语言版本中的对等 book 页面

#### Scenario: Book header language switch keeps the chapter target
- **WHEN** 读者位于一个在两个版本中都存在相同 slug 的章节页，并从 book header 激活语言切换
- **THEN** 目标页在另一语言版本前缀下打开相同的章节 slug

#### Scenario: Landing and legal pages switch to their edition peers
- **WHEN** 读者从 landing page、legal page 或 chapter-library page 激活语言切换
- **THEN** 目标页打开另一语言版本中的对应页面，而不是退回到通用首页
