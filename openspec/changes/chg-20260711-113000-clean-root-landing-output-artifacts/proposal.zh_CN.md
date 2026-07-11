## Why

仓库根目录仍然跟踪着一套过时的 landing 输出（`index.html` 和 `fr/index.html`），但 GitHub Pages 实际只部署 `public/` 目录。这两份文件仍包含旧的 PNG landing 引用，会干扰资源盘点，也让源码里长期存在第二套误导性的输出面。

这次清理要做两件事：删除这些已经不参与发布的根目录产物；同时让独立 landing 生成命令默认写到 `public/`，避免后续手工执行时又把根目录产物重新生成回来。

## What Changes

- 删除不参与部署的根目录 tracked landing 输出。
- 把独立 landing 生成脚本的默认输出位置从仓库根目录改为 `public/`。
- 更新 `package.json` 中 landing、legal、chapters 的脚本别名，显式传入 `--output-root public`。
- 增加回归覆盖，保证根目录 landing 输出不会重新进入源码树，并继续约束 landing 页面只引用允许保留的 PNG。

## Capabilities

### New Capabilities
- `root-landing-output-cleanup`：仓库不再保留根目录历史 landing 输出作为 tracked 文件。

### Modified Capabilities
- `landing-site-build`：独立 landing 生成入口默认写入部署目录 `public/`，而不是仓库根目录。

## Impact

- 受影响脚本：
  - `scripts/generate-index-page.mjs`
  - `scripts/generate-legal-pages.mjs`
  - `scripts/generate-chapters-page.mjs`
  - `scripts/test-site-render.sh`
- 受影响脚本别名：
  - `package.json`
- 受影响清理目标：
  - `index.html`
  - `fr/index.html`
- 受影响回归覆盖：
  - `tests/test_public_editions.py`
