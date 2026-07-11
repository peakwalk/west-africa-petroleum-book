## Why

landing shell 现在仍然用同一张 `240x256` 的 PNG 同时承担浏览器 tab icon、shortcut icon 和 Apple touch icon。这张图大约 `45KB`，导致所有 landing 路由在普通浏览访问时都为 favicon 支付了不必要的字节，而浏览器标签页真正常用的只是一张 `32x32` 资产。

## What Changes

- 把 landing favicon 交付拆成一个更小的 tab favicon PNG 和一个独立的 Apple touch icon PNG。
- 更新共享 landing 头部生成器，让 `rel="icon"` 和 `rel="shortcut icon"` 引用更小的 tab icon，而 `rel="apple-touch-icon"` 改用单独的大一点的 PNG。
- 保持 favicon 继续走 PNG 资产以兼容浏览器，不把 favicon 交付切到 WebP。
- 刷新 landing 验证，让生成页一旦回退到旧的 oversized favicon 路径就直接失败。

## Capabilities

### New Capabilities
- `landing-favicon-delivery`：landing 页面使用更小的 tab favicon PNG 加独立 Apple touch icon PNG，而不是继续复用一张 oversized shared favicon 资源。

### Modified Capabilities
- None.

## Impact

- 受影响的 landing 生成源码：`scripts/shared/landing-shell.mjs`
- 受影响的 landing 源资源：`assets/images/upstream-atlas-favicon.png`、`assets/images/upstream-atlas-favicon-32.png`、`assets/images/upstream-atlas-apple-touch-icon.png`
- 受影响的验证：`tests/test_public_editions.py`、`scripts/test-site-render.sh`
- 重建后受影响的生成产物：`public/index.html`、`public/fr/index.html`、`public/chapters/index.html`、`public/fr/chapters/index.html`、`public/*legal*.html`，以及复制到 `public/assets/images/` 和 `public/fr/assets/images/` 下的 favicon 资源
