## ADDED Requirements

### Requirement: Preview rebuilds after render-affecting source changes
`npm run preview` MUST 在启动后持续运行，并且 MUST 在会影响渲染的源码文件变化时重新构建已装配站点。

#### Scenario: Styles or content change during preview
- **WHEN** 用户在 `npm run preview` 运行期间修改了被监听的样式表、模板、章节、图片或 preview 构建脚本
- **THEN** preview 工作流重新执行 assembled-site 构建
- **AND** 刷新后的输出被写回现有的 `public/` 目录树

#### Scenario: A second change arrives during an active rebuild
- **WHEN** preview 工作流已经在重建时，又有另一个被监听文件发生变化
- **THEN** 工作流不会并发启动第二个重建
- **AND** 它会在当前重建结束后再安排一次补跑重建

### Requirement: Preview pages reload only after successful rebuilds
Preview server 提供的页面 MUST 在成功重建后自动刷新，并且 MUST 在重建失败时避免强制刷新。

#### Scenario: Successful rebuild advances the preview session
- **WHEN** 被监听的变更触发了一次成功的 preview 重建
- **THEN** 已打开的 preview 页面会收到变化后的 reload token
- **AND** 浏览器会自动刷新当前页面

#### Scenario: Failed rebuild keeps the previous page stable
- **WHEN** 被监听的变更触发了一次失败的重建
- **THEN** preview 工作流继续提供上一次成功的 `public/` 输出
- **AND** 已打开的 preview 页面不会自动刷新到损坏状态

### Requirement: Preview-only reload code does not alter published files on disk
浏览器自动刷新机制 MUST 保持为仅在 preview 服务阶段生效的能力，并且 MUST NOT 改写 `public/` 下已构建好的 HTML 文件。

#### Scenario: Reload helper is injected only while serving preview HTML
- **WHEN** 在启用 preview 自动刷新的情况下，preview server 返回一个 HTML 页面
- **THEN** 该响应包含 preview reload helper
- **AND** 磁盘上对应的 HTML 文件保持不变
