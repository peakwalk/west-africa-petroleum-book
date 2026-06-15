## ADDED Requirements

### Requirement: Shared edition registry
构建系统 MUST 通过一个受版本控制的共享 registry 解析所有版本，而不是继续把英文路径写死。该 registry MUST 为每个版本定义 locale code、公开路由前缀、手稿别名路径、Markdown 源根目录、legal 内容根目录、figure 根目录和 book 配置。

#### Scenario: Build scripts resolve the French edition from config
- **WHEN** 某个构建或校验命令以法文版为目标运行
- **THEN** 该命令从共享 edition registry 读取法文源目录、手稿别名和输出前缀，而不是写死 `src` 或英文手稿路径

#### Scenario: New edition inputs remain additive
- **WHEN** registry 同时包含 `en` 与 `fr`
- **THEN** 生成逻辑对两个版本复用同一组脚本入口，而不是再复制出一整套第二份构建脚本

### Requirement: Mirrored source topology across editions
法文版 MUST 与英文版保持一致的源拓扑，包括 summary 结构、chapter slug、legal page key 和 figure 编号。面向用户的标题和正文可以按 locale 变化，但内部 slug 和 figure identifier MUST 在两个版本之间保持对齐。

#### Scenario: Chapter slugs are stable across locales
- **WHEN** 对比英文与法文章节源树
- **THEN** 尽管渲染标题语言不同，但两个版本中的每个章节都能通过相同的 slug 路径访问

#### Scenario: Figure numbers remain aligned across locales
- **WHEN** 为两个版本生成 figure manifest
- **THEN** 相同的 figure number 在各自版本中都映射到该版本自己的 caption 与资源集合

### Requirement: Locale-scoped manuscript and figure assets
每个版本 MUST 使用自己的 canonical DOCX/PDF 别名路径，以及自己的 figure-manifest 和渲染后 figure 资源。法文版 MUST NOT 复用英文版的 figure-manifest 或英文 text-replacement map 作为真值来源。

#### Scenario: French figure rendering reads French manuscript aliases
- **WHEN** 执行法文 figure 渲染或清单生成命令
- **THEN** 该命令读取法文 DOCX/PDF 别名路径，并向法文 figure 根目录写入或基于其执行校验

#### Scenario: English text replacement is not applied to French figures
- **WHEN** 某个法文 figure 原生包含法文 chart 或 document 标签
- **THEN** 除非法文版明确定义自己的 replacement map，否则渲染流水线保留法文标签

#### Scenario: French figure root is isolated from the English shared tree
- **WHEN** 法文版执行 figure 构建或校验
- **THEN** 它使用真实的 `src-fr/images` 根目录，而不是继续指向或共享 `src/images`

#### Scenario: French published assets converge to French manuscript output
- **WHEN** 某个法文发布图片进入 release 定稿状态
- **THEN** 它必须按该 figure kind 从法文 DOCX/PDF 输入渲染，而不是从英文已发布图片树复制
