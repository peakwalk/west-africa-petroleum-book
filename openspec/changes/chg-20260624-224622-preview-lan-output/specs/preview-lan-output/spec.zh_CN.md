## ADDED Requirements

### Requirement: Preview startup announces a LAN-reachable URL by default
`npm run preview` MUST 在默认绑定配置下输出一个局域网可访问的 URL。

#### Scenario: Default preview output shows a LAN-friendly address
- **WHEN** 用户在没有覆盖 host 的情况下运行 `npm run preview`
- **THEN** preview server 绑定到 `0.0.0.0`
- **AND** 启动输出显示一个局域网可访问的地址，而不是 `127.0.0.1` 或 `0.0.0.0`

#### Scenario: Preview server banner matches the wrapper output
- **WHEN** preview server 启动
- **THEN** Python server 的 banner 显示与 shell wrapper 输出相同的 display host 和端口

### Requirement: Preview startup remains override-friendly
`npm run preview` MUST 保留对特殊本地网络环境的显式覆盖路径。

#### Scenario: Explicit display-host override is honored
- **WHEN** 用户设置了显式的 preview display-host 覆盖值
- **THEN** 启动输出使用该覆盖值
- **AND** Python server banner 使用同一个覆盖值
