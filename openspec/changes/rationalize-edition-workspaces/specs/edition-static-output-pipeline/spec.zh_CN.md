## ADDED Requirements

### Requirement: 静态站点生成器必须直接发布到 assembled public tree
landing、legal 和 chapter-library 生成器 MUST 按照各语言版本的 route prefix 直接将输出写入 `public/`，而不是先在仓库根目录或 `fr/` 下生成受版本控制的静态 HTML。

#### Scenario: 英文公共页面直接生成到 public 根路径
- **WHEN** 站点构建成功完成
- **THEN** 英文 landing 页面、legal 页面和 chapter-library 页面存在于 `public/` 下，并且构建不再依赖根目录受版本控制的 HTML 作为输入

#### Scenario: 法文公共页面直接生成到带前缀的 public 根路径
- **WHEN** 站点构建成功完成
- **THEN** 法文 landing 页面、legal 页面和 chapter-library 页面存在于 `public/fr/` 下，并且构建不再依赖受版本控制的 `fr/` HTML 作为输入

### Requirement: mdBook 输出必须从 edition roots 组装到兼容当前路由的发布目标
构建流水线 MUST 从各自的 edition 工作区运行 mdBook 构建，并将 reader 输出发布到 `public/<routePrefix>/book`；默认英文版使用 `public/book`，法文版使用 `public/fr/book`。

#### Scenario: 默认语言 book 输出保持当前英文路由
- **WHEN** 英文 edition build 运行
- **THEN** 即使英文源码已经迁移到 `editions/en/`，reader 输出仍发布到 `public/book/`

#### Scenario: 法文 book 输出保持当前带前缀路由
- **WHEN** 法文 edition build 运行
- **THEN** 即使法文源码已经迁移到 `editions/fr/`，reader 输出仍发布到 `public/fr/book/`

### Requirement: `public/` 之外不得继续保留受版本控制的生成发布页面
当迁移完成后，仓库 MUST 将 `public/` 视为唯一的生成发布产物目录，并且 MUST NOT 在 `public/` 之外继续依赖受版本控制的 landing、legal 或 chapter-library 生成 HTML。

#### Scenario: 仓库根目录不再作为生成发布页面来源
- **WHEN** 贡献者在迁移清理完成后检查仓库
- **THEN** 根目录生成 landing/legal/chapter HTML 已不存在，并且构建不再依赖这些文件

#### Scenario: 法文前缀静态页面不再在 public 之外被版本控制
- **WHEN** 贡献者在迁移清理完成后检查仓库
- **THEN** 除了 assembled `public/fr/` 发布产物之外，仓库中不再存在受版本控制的 `fr/` 静态页面树
