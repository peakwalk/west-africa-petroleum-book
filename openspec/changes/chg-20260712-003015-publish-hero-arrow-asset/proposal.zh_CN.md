## 背景与动机

英文首页 Hero 按钮引用了 `hero-arrow.svg`，但静态站点构建没有发布该资源。访问者会收到 404，预期箭头不显示；源资源和 CSS 引用本身均存在。

## 变更内容

- 将 `assets/icons/homepage/hero-arrow.svg` 作为英文首页资源发布。
- 将禁止生成该资源的过期站点渲染断言替换为必须生成的断言。
- 验证构建后的英文首页加载箭头时不再出现 404，同时保持按钮标记和导航不变。

## 能力

### 新增能力

- `homepage-hero-arrow-asset-delivery`：交付英文 Hero 按钮样式所引用的资源，并验证其在生成站点中的可用性。

### 修改的能力

无。

## 影响范围

- 受影响源文件：`scripts/build_site.mjs` 与 `scripts/test-site-render.sh`。
- 受影响生成产物：`public/assets/icons/homepage/hero-arrow.svg`。
- 不改变 URL、按钮文案、导航、CSS 选择器、依赖、章节或法文首页。
