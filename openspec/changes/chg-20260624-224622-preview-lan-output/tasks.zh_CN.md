## 1. OpenSpec 与源码级检查

- [x] 1.1 为局域网友好的 preview 启动输出补齐 proposal、design 和 `preview-lan-output` capability spec。
- [x] 1.2 为 preview 的 bind host、display host 和启动 banner 契约补充或更新源码级断言。

## 2. Preview 启动行为

- [x] 2.1 让 `scripts/preview.sh` 默认绑定到 `0.0.0.0`。
- [x] 2.2 当绑定地址为 wildcard 时探测一个局域网可访问的 display host，并提供一个显式覆盖入口以便稳定测试。
- [x] 2.3 将 display host 传递给 `scripts/preview_server.py`，使其 banner 与 wrapper 输出一致。

## 3. 验证

- [x] 3.1 运行针对性的 preview build / startup 测试。
- [x] 3.2 运行 `sh scripts/test-site-render.sh`。
- [x] 3.3 运行最小必要的 site build/test 命令，确认 preview 变更不会影响已构建的 reader 输出。
