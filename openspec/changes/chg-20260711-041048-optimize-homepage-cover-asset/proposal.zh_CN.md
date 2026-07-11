## Why

landing 首页当前仍然让 current-edition 卡片使用一张 `1024x1536`、约 `1.8MB` 的 PNG 封面图，即使这个卡片里的实际显示尺寸远小于原图，而且位置也在主 hero 之后。这个非关键图片单独就占掉了首页大部分图片字节，不值得继续用全尺寸 PNG 交付。

## What Changes

- 为首页 current-edition 卡片增加一份仓库内维护的优化版 WebP 封面资源。
- 更新共享 homepage 生成器，让 current-edition 封面改用优化版 WebP，并带上非关键资源的加载提示。
- 保持首页地图面板继续走现有 SVG 合约，不改其他 landing 图片格式。
- 刷新首页验证，让构建产物一旦回退到沉重的 PNG 封面资源就直接失败。

## Capabilities

### New Capabilities
- `homepage-cover-asset-delivery`：英文 landing 首页用优化后的 WebP 资源渲染 current-edition 封面卡片，并以非关键资源方式加载。

### Modified Capabilities
- None.

## Impact

- 受影响的首页生成源码：`scripts/shared/homepage-content.mjs`
- 受影响的首页源资源：`assets/images/upstream-atlas-hero-book.png`、`assets/images/upstream-atlas-hero-book.webp`
- 受影响的验证：`tests/test_public_editions.py`、`scripts/test-site-render.sh`
- 重建后受影响的生成产物：`public/index.html`、`public/assets/images/upstream-atlas-hero-book.webp`、`public/fr/assets/images/upstream-atlas-hero-book.webp`
