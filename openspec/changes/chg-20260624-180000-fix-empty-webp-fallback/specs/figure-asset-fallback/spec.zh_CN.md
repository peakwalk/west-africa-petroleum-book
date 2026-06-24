## ADDED Requirements

### Requirement: Published figure asset selection skips empty preferred files
Figure inventory 发布器在同一 figure stem 下遇到 0 字节候选资源时 MUST 跳过它，并按既有扩展名优先级回退到下一个非空的可发布格式。

#### Scenario: Empty WebP falls back to PNG
- **WHEN** `figure-011.webp` 存在但文件大小为 0 字节
- **AND** `figure-011.png` 存在且非空
- **THEN** Figure 11 的 published asset candidates 选择 `figure-011.png`，而不是这个空 WebP

### Requirement: Figure coverage validation rejects empty published assets
DOCX figure coverage checker 在 Markdown 引用的资源或 manifest 选中的发布资源虽然存在但文件大小为 0 字节时 MUST 直接失败。

#### Scenario: Empty Markdown target is reported
- **WHEN** 某个章节 Markdown 图片引用指向一个 0 字节的 figure 资源
- **THEN** coverage checker 将该引用报告为“空资源失败”

#### Scenario: Empty manifest-selected asset is reported
- **WHEN** 某个 figure manifest 记录选中的 published asset 文件大小为 0 字节
- **THEN** coverage checker 将该 manifest 资源报告为“空资源失败”
