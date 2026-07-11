## 背景与原因

UA-19 指出英文在线图书的图 9、图 41 和图 69 存在技术性不准确之处。Jira 附件仍使用开发阶段的旧文件名，比在线图号小 1；若将附件名直接当作发布资产名，会错误覆盖不相关的图 8、图 40 和图 68。

本变更将在保持图注、引用、视觉风格以及英文版和法文版完整性的前提下，修正这三张技术图件。

## 变更内容

- 使用对应的 UA-19 附件图稿作为源图，替换英文版在线图 9、图 41 和图 69 的发布图件：
  - Jira `figure-008.png` -> 在线图 9 -> `figure-009.png` 与 `figure-009.webp`
  - Jira `figure-040.png` -> 在线图 41 -> `figure-041.png` 与 `figure-041.webp`
  - Jira `figure-068.png` -> 在线图 69 -> `figure-069.png` 与 `figure-069.webp`
- 按 UA-19 修正三张图的术语、工作流方向和 PSC 收入分配流程。
- 保留现有英文版章节引用、图注、在线图号及 Upstream Atlas 视觉风格。
- 重建英文图件元数据，并增加针对“附件到发布资产”映射的回归检查。
- 在实施前保存可复现的基线截图，并在实施后按相同条件保存更新截图，供成对人工评审。

## 能力范围

### 新增能力

- `technical-figure-corrections`：当 Jira 源图文件名与在线图件资产名不一致时，安全发布经过技术评审的图件修正。

### 修改的既有能力

- 无。

## 影响范围

- 受影响资产：`editions/en/content/images/figure-009.{png,webp}`、`figure-041.{png,webp}` 与 `figure-069.{png,webp}`。
- 受影响元数据和验证：英文图件清单及聚焦的图件引用测试。
- 评审证据：`output/playwright/ua-19-technical-figure-corrections/` 下的成对截图。
- 不在范围内：`public/`、英文版章节 Markdown、法文版资产，以及图 8、图 40、图 68。
