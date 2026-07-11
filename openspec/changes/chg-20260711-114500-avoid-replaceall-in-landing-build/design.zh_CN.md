## Overview

这里的 landing 构建只需要做 HTML 转义，没有必要依赖 `replaceAll`。同样的行为完全可以用全局正则 `.replace(...)` 表达，而且能兼容更老的运行时。

## Decisions

1. 保持转义 helper 继续留在 `homepage-outline-icons.mjs` 本地。
2. 把每个 `replaceAll` 改成等价的全局 `.replace(...)`。
3. 在站点渲染回归里增加断言，禁止这个 helper 重新出现 `replaceAll(`。

## Verification

- 运行 `npm run build:site`
- 启动 `./scripts/preview.sh`，确认 preview 能输出 ready 信息
- 运行 `npm run test:site`
