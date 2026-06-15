## ADDED Requirements

### Requirement: Locale-aware DOCX chapter extraction
Parity validation MUST 支持按语言区分的章节标记与锚点规则，从而让每个版本都能从自己的 DOCX 手稿中完成提取。法文提取 MUST NOT 依赖英文专用的 `Chapter N:` 标记。

#### Scenario: French chapter detection uses French chapter rules
- **WHEN** 法文 parity 命令从法文 DOCX 中提取章节边界
- **THEN** 它能识别所有预期的法文章节和前后置部分，而不依赖英文的 chapter-marker 正则

#### Scenario: Edition-specific anchor rules are configurable
- **WHEN** 某个 parity 命令为某个版本解析开始或结束锚点
- **THEN** 该命令从 edition-aware 的校验输入中读取该版本的 chapter-title 与 anchor 配置

### Requirement: Edition-scoped figure validation
Figure inventory、manifest generation 和 figure-validation 命令 MUST 针对目标版本自己的 manuscript、summary、chapter tree 与 figure root 运行。若法文 figure 校验失败，报告 MUST 指向法文资源和法文章节路径。

#### Scenario: Figure validation targets the French source tree
- **WHEN** 法文 figure-validation 命令运行
- **THEN** 它读取法文 summary 与法文章节目录，并针对法文 figure-manifest 进行报告

#### Scenario: Validation reports edition-specific paths
- **WHEN** 某个带版本作用域的 figure 或 parity 检查失败
- **THEN** 输出会标明失败的版本以及对应的 locale-specific 章节或 figure 路径

#### Scenario: French figure inventory supports localized chapter and index formats
- **WHEN** 法文 DOCX 使用 `Chapitre N` 标记，且法文 figure index 使用 `Figure N :` 这种标题格式
- **THEN** inventory 与 coverage checks 仍然能把每个法文 figure number 映射到正确的法文章节路径

### Requirement: Dual-edition release gating
站点验证与 Pages 发布 MUST 在英文版或法文版任一构建或校验失败时整体失败。因此，成功发布 MUST 意味着两个版本都通过了所需的 parity、figure 与 render 检查。

#### Scenario: English success plus French failure blocks release
- **WHEN** 英文版通过，但法文版在 parity、figure 或 render 检查上失败
- **THEN** 顶层站点验证与发布工作流失败

#### Scenario: Both editions passing allows release
- **WHEN** 两个版本都通过所需的构建与校验命令
- **THEN** 顶层验证与发布工作流成功
