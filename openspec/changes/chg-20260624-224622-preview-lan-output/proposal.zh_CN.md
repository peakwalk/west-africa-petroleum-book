## Why

当前 `npm run preview` 只针对 loopback 使用场景进行了优化。它默认绑定并输出 `127.0.0.1`，导致手机联调很不方便，尽管 preview 内容本身完全可以在本地局域网中临时暴露用于人工验证。

## What Changes

- 将 preview server 的默认绑定地址改为 `0.0.0.0`。
- 在启动输出里探测并打印一个可从局域网访问的显示地址。
- 保留显式 host 覆盖能力，并新增显式 display-host 覆盖能力，以便做确定性的测试。
- 让 preview server 自身的 banner 也打印与 shell wrapper 一致的局域网可访问地址。

## Capabilities

### New Capabilities
- `preview-lan-output`：`npm run preview` 会输出一个可从局域网访问的 URL，便于本地网络中的手机测试，同时仍然服务同一份构建产物。

### Modified Capabilities
- None.

## Impact

- 受影响源码：`scripts/preview.sh`、`scripts/preview_server.py`、`scripts/test-preview-build.sh`、`scripts/test-site-render.sh`
- 不涉及书稿内容、figure manifest 或发布资源变更
