## Context

当前 preview 工作流本质上是一个很薄的 shell wrapper：先执行 `npm run build:site`，再启动一个小型 Python HTTP server。由于是两层输出，用户启动时会看到两个入口提示：

- `scripts/preview.sh` 打印 ready URLs
- `scripts/preview_server.py` 打印实际 serving banner

如果只改其中一层，用户看到的地址就会不一致。因此同一个“显示地址”必须贯穿这两层。

## Goals / Non-Goals

**Goals:**
- 让 `npm run preview` 默认就适合在同一局域网内做手机测试。
- 输出一个第二台设备真的可以访问的地址。
- 为启动输出保留确定性的测试覆盖。
- 保留显式 host 覆盖能力。

**Non-Goals:**
- 发现或优选多个网络接口。
- 实现 mDNS、二维码或自动设备配对。
- 修改缓存头、路由或构建行为。

## Decisions

### Decision: 默认绑定到 `0.0.0.0`
除非用户显式覆盖 `HOST`，否则 preview server 应监听所有 IPv4 接口。这样同一局域网设备测试就能成为默认工作流，而不需要用户额外记住环境变量。

考虑过的替代方案：
- 保持 `127.0.0.1` 为默认值，只在文档里说明 `HOST=0.0.0.0`。否决，因为这里的问题本质上就是默认行为不方便。

### Decision: 区分 bind host 和 display host
当绑定地址是 `0.0.0.0` 这样的 wildcard 时，它并不是用户应该复制到手机里的地址。因此 shell wrapper 需要单独计算一个 display host，并把它传给 Python server，这样两处启动输出才能保持一致。

考虑过的替代方案：
- 直接把 wildcard 地址原样打印出来。否决，因为 `0.0.0.0` 不是手机测试可用的目标地址。

### Decision: 为测试提供显式 display-host 覆盖
局域网 IP 自动探测天然依赖运行环境。为了让自动化检查稳定，工作流应提供一个 `PREVIEW_DISPLAY_HOST` 覆盖入口。

考虑过的替代方案：
- 只测试自动探测路径。否决，因为 CI 和本地 shell 的网卡可见性经常不同。

## Risks / Trade-offs

- [自动探测在特殊机器上可能挑错网卡] -> 允许显式 `PREVIEW_DISPLAY_HOST` 和 `HOST` 覆盖。
- [绑定到所有接口比 loopback 更开放] -> 接受这个取舍，因为这里的 preview 工作流本来就明确需要局域网访问，而且服务的仍然只是本地静态产物。
- [某些机器上的 UDP 探测可能失败] -> 回退到 bind host 或 loopback 安全输出，而不是直接报错。

## Migration Plan

1. 为“局域网友好的 preview 输出”补齐 OpenSpec proposal、design、tasks 和 capability spec。
2. 更新 `scripts/preview.sh`，使其默认绑定 `0.0.0.0` 并计算 display host。
3. 更新 `scripts/preview_server.py`，使其接收并打印 display host。
4. 扩展 preview 启动断言，覆盖 LAN 输出契约。
5. 验证 preview build 路径、site-render 断言和站点构建。
