## Why

当前 `npm run preview` 会在 landing 生成阶段失败，因为某些本地 JavaScript 运行时不提供 `String.prototype.replaceAll`。报错发生在 `scripts/shared/homepage-outline-icons.mjs`，因此 preview server 还没起来，landing 构建就已经中断。

这次修复应该尽量小：保留同样的转义行为，但不要再让 landing 构建链路依赖 `replaceAll`。

## What Changes

- 把 `scripts/shared/homepage-outline-icons.mjs` 里的 `replaceAll` 改成兼容旧运行时的全局替换写法。
- 增加一条回归断言，防止 landing 构建链路重新引入 `replaceAll`。

## Capabilities

### Modified Capabilities
- `landing-site-build`：landing 生成继续兼容 preview 和本地构建入口可能使用的旧 JavaScript 运行时。

## Impact

- 受影响源码：
  - `scripts/shared/homepage-outline-icons.mjs`
- 受影响验证：
  - `scripts/test-site-render.sh`
