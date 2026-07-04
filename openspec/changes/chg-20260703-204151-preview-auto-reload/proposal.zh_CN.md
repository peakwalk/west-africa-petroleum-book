## Why

`npm run preview` 目前只会执行一次 `build:site`，然后启动静态文件服务。只要 CSS、章节内容、模板、图片或脚本中任何会影响渲染的文件发生变化，就必须手动停止进程再重新启动，这让日常的版式和内容迭代变得很低效。

## What Changes

- 在 `npm run preview` 运行期间增加一个 preview watch 进程，监听会影响渲染的源码路径。
- 相关文件变化后自动重新执行 `npm run build:site`，并通过串行重建避免多次编辑互相踩坏已装配好的输出。
- 增加一个仅用于 preview 的浏览器自动刷新机制，使已打开的 HTML 页面在成功重建后自动刷新。
- 保持现有 preview 路由、局域网启动输出和静态 `public/` 产物模型不变。
- 扩展 preview 相关校验，覆盖 watch / reload 契约。

## Capabilities

### New Capabilities
- `preview-auto-reload`：`npm run preview` 监听会影响渲染的源码文件，在相关变更后重建已装配站点，并在成功重建后自动刷新已连接的 preview 页面。

### Modified Capabilities
- None.

## Impact

- 受影响源码：`scripts/preview.sh`、`scripts/preview_server.py`、`scripts/` 下新增的 preview watch 编排脚本
- 受影响校验：`scripts/test-preview-build.sh`、`scripts/test-preview-cache.sh`、`scripts/test-site-render.sh`
- 预期不引入新的外部运行时依赖
- 不打算改变发布路由、生产 HTML 输出或 figure / 内容源码结构
