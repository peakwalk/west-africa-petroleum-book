## Why

当前 `/book/` reader 里的 figure 仍然以阅读宽度展示。对于密集图表、SVG 图和多面板 figure，用户很难看清细节，而自定义页内 viewer 方案的稳定成本已经超过了它当前的收益。

## What Changes

- 为 `/book/` reader 里的正文 figure 卡片添加一个轻量运行时增强。
- 复用现有生成后的 figure-card 标记，使单图和多图 figure 都能工作，而不需要修改章节 Markdown 或 figure manifest。
- 点击图片后在新浏览器标签页中打开原图资源，并直接复用浏览器原生的图片查看、平移和缩放能力。
- 保留对符合条件图片的键盘可访问激活能力。
- 把行为范围限制在 `.reader-article .figure-card img`；不作用于封面、导航、落地页或装饰性图片。
- 移除自定义 overlay viewer 实现以及 vendored pan/zoom 依赖。

## Capabilities

### New Capabilities
- `book-reader-image-zoom`：`/book/` reader 允许用户通过在新标签页打开原图来查看正文 figure 图片，同时不影响非正文图片。

### Modified Capabilities
- None.

## Impact

- 受影响的源文件：`editions/en/book.toml`、`editions/fr/book.toml`、`theme/custom.js`、`theme/custom.css`、`tests/test_theme_custom_css.py`、`scripts/test-site-render.sh`
- 通过运行时增强影响的生成输出：`/book/chapters/*.html`
- 移除了已 check-in 的浏览器依赖，回到仅依赖主题本地 JavaScript 的实现
- 这个行为不需要修改 edition 章节 Markdown、figure manifest 或已发布资源命名
