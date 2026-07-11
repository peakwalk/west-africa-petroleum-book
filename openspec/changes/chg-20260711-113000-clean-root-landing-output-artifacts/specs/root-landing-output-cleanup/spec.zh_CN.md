## ADDED Requirements

### Requirement: 根目录 landing 输出不得继续进入源码树

仓库 MUST NOT 继续保留与已部署 `public/` 站点表面重复的根目录 tracked landing HTML 输出。

#### Scenario: 根目录 landing 输出已从仓库清理

- **WHEN** 在清理后检查仓库树
- **THEN** 仓库根目录下不存在 `index.html`
- **AND** 根目录 locale 子目录下不存在 `fr/index.html`

### Requirement: 独立 landing 生成入口默认写入部署输出根目录

除非调用方显式覆盖目标位置，独立 landing 生成命令 MUST 写入部署输出树。

#### Scenario: package 脚本别名默认指向部署输出树

- **WHEN** 贡献者不额外传参直接运行 landing 生成脚本别名
- **THEN** `build:index`、`build:legal`、`build:chapters` 默认目标为 `public/`
- **AND** 生成的 landing 页面仍只引用 `upstream-atlas-favicon-32.png`、`upstream-atlas-apple-touch-icon.png` 和 `upstream-atlas-icon.png` 这三个 landing PNG 资源
