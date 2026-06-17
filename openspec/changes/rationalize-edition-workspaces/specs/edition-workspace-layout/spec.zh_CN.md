## ADDED Requirements

### Requirement: 语言自有输入必须组织在单一 edition 根目录下
仓库 MUST 将每个语言版本自己的 mdBook 配置、locale catalog、landing/legal 源内容、Markdown 正文、figure 资源以及 figure manifest 组织在统一的 `editions/<locale>/` 根目录下，并使用共享的内部目录结构。

#### Scenario: 英文与法文 edition roots 使用同一工作区形状
- **WHEN** 贡献者检查 `editions/en/` 与 `editions/fr/`
- **THEN** 两个根目录都包含各自的 `book.toml`、`locale.json`、`site/` 和 `content/` 目录

#### Scenario: 语言自有内容都位于 edition 根目录之下
- **WHEN** 贡献者检查任一 edition 工作区
- **THEN** 该语言版本的 `SUMMARY.md`、章节 Markdown、locale-specific legal 内容、figure 资源和 `figure-manifest.json` 都位于该 edition 根目录之下，而不是继续分散在互不相关的顶层目录中

### Requirement: edition 配置必须从 edition root 派生路径
共享 edition registry MUST 通过 `editionRoot` 约定声明每个语言版本，并且 MUST 从该根目录派生 book、site、content、legal、chapter、locale catalog、figure root 和 figure manifest 路径，而不是独立保存每一条派生路径。

#### Scenario: registry 通过单一根目录加载语言版本
- **WHEN** 构建或校验代码加载一个 edition 定义
- **THEN** 代码会从该配置的 `editionRoot` 解析出该语言版本的 book config、site 内容、Markdown 内容、locale catalog、figure root 和 figure manifest

#### Scenario: Node 与 Python loader 解析同一套 edition 结构
- **WHEN** Node 侧站点生成器与 Python 校验脚本加载同一个语言版本
- **THEN** 两个运行时都会为该版本解析出一致的 book config、summary、chapters、legal 内容、figure root 与 figure manifest 路径

### Requirement: 迁移完成后必须退役旧的语言源码根
当 edition-root 拓扑成为正式结构后，仓库 MUST NOT 再依赖 `src-fr/`、`books/fr/`、根 `book.toml` 或 `config/locales/*.json` 这类分裂式旧路径来提供语言自有输入。

#### Scenario: 构建输入只来自 edition 工作区
- **WHEN** 迁移后的 assembled site build 运行
- **THEN** 它会从 `editions/<locale>/` 根目录读取语言自有输入，而不是依赖这些根目录之外的遗留语言专属源码路径

#### Scenario: edition 工作区可以扩展到新的语言版本
- **WHEN** 维护者未来需要新增一个语言版本
- **THEN** 维护者只需要创建一个新的 `editions/<locale>/` 工作区并在 registry 中注册其 `editionRoot`，而不需要再引入新的顶层命名约定
