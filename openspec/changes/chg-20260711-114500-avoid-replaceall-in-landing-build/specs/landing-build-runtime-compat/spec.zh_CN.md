## MODIFIED Requirements

### Requirement: Landing build helpers MUST 保持对 preview 运行时的兼容性

只要某个 helper 会被 landing 生成入口调用，它就 MUST 避免使用在较旧本地 preview 运行时下会导致 `npm run preview` 失败的 JavaScript 字符串 API。

#### Scenario: outline icon 转义逻辑不依赖 replaceAll

- **WHEN** landing 构建渲染首页 outline icon
- **THEN** `scripts/shared/homepage-outline-icons.mjs` 不调用 `replaceAll`
- **AND** landing 生成仍会在内联 SVG 标记前对 class name 和 icon name 做 HTML 转义
