## Overview

当前部署站点已经只有一个规范输出根目录：`public/`。这次清理要把独立 landing 生成入口也对齐到这个约束上，并删除那两份不被任何构建或部署流程消费的根目录历史 HTML 文件。

## Decisions

1. 直接删除 tracked 的根目录 landing 输出，而不是继续维持它们同步。
2. 保留 `--output-root` 覆盖能力，供测试和构建编排继续使用。
3. 把三个独立生成脚本的默认输出根目录改为 `public/`。
4. 在 `package.json` 里显式写出目标目录，让默认行为一眼可见。
5. 增加回归断言：只要根目录 landing 输出重新出现，或 landing 页面重新引用额外 PNG，就直接失败。

## Non-Goals

- 不改动 `book/` 或 `public/book/` 下的 mdBook reader 输出。
- 不改动已部署 landing 的页面结构或 locale 路由。
- 不在这次清理里调整 book theme 的 favicon 行为。

## Verification

- 运行 `python3 -m unittest tests.test_public_editions`
- 运行 `npm run build:site`
- 运行 `npm run test:site`
