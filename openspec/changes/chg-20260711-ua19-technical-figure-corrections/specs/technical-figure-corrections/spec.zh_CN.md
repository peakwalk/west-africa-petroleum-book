## 新增需求

### 需求：在线图号决定发布资产名
当 UA-19 源图使用开发阶段文件名时，系统必须以在线图号作为英文发布资产标识。必要映射为：Jira `figure-008.png` 对应在线图 9 和 `figure-009.{png,webp}`；Jira `figure-040.png` 对应在线图 41 和 `figure-041.{png,webp}`；Jira `figure-068.png` 对应在线图 69 和 `figure-069.{png,webp}`。

#### 场景：低一号 Jira 源图准备发布
- **当** 实施者收到 UA-19 的 `figure-008.png`、`figure-040.png` 和 `figure-068.png` 附件
- **则** 修订后的英文资产分别以 `figure-009`、`figure-041` 和 `figure-069` 保存并发布

#### 场景：相邻图件受到保护
- **当** 发布三份修订后的资产
- **则** 在线图 8、图 40 和图 68 的资产不会被 Jira 附件替换

### 需求：图 9 使用经评审的石油产品术语
发布的在线图 9 必须将“Heavy Gasoline (Intermediate)”替换为“Heavy Naphtha”，将“Kerosene”替换为“Jet Fuel (Kerosene)”。必须保留既有产品顺序、视觉风格、布局和图注。

#### 场景：读者查看在线图 9
- **当** 英文图 9 在图书中渲染
- **则** 两个经评审的术语出现在原有产品位置，图注和产品顺序不变

### 需求：图 41 表达经评审的建模流程
发布的在线图 41 必须将 Reservoir Models 和 Reservoir Understanding 表达为 Integration and Modelling 的输出，并作为 Evaluation and Recovery Options 的输入。所有工作流箭头必须有有效起点和终点，框 2 右侧的冗余箭头必须不存在。

#### 场景：读者沿图 41 跟踪工作流
- **当** 英文图 41 在图书中渲染
- **则** 建模输出流入 Evaluation and Recovery Options，且不显示悬空箭头

### 需求：图 69 表达经评审的 PSC 收入流
发布的在线图 69 必须按逻辑顺序展示 Gross Revenue、Recoverable Costs (Cost Oil / Cost Gas)、Profit Oil / Profit Gas、Government Share 和 Contractor Share。Recoverable Costs 必须列出 Exploration、Development、Operating 以及 Abandonment / Decommissioning Costs。图中必须将“Uses of Government Take”改为“Components of Government Take”，并将 Profit Oil / Profit Gas 说明更新为“Remaining revenue after recovery of allowable costs.”

#### 场景：读者沿图 69 跟踪收入分配
- **当** 英文图 69 在图书中渲染
- **则** Recoverable Costs 与 Profit Oil / Profit Gas 清楚分离，且 Government Share 与 Contractor Share 源自 Profit Oil / Profit Gas

### 需求：修订后图件可发布且可追溯
实施必须保留修订后的 PNG 源资产，生成非空的英文 WebP 发布资产，重建英文图件清单，并保留现有章节引用和图注。不得手动编辑 `public/`，也不得修改法文版资产。

#### 场景：图件更新后重新构建英文站点
- **当** 项目构建英文站点并运行图件校验
- **则** 清单和图件检查通过，生成页面引用更新后的 009、041 和 069 WebP 资产

### 需求：保存成对的视觉评审证据
替换目标图件前，实施必须在构建后的阅读器中为每张受影响英文图保存基线截图。实施并重建站点后，必须使用相同浏览器引擎、路由、视口、整页设置和按图命名方式保存对应的更新截图。基线与更新产物必须保存在 `output/playwright/ua-19-technical-figure-corrections/` 下，并一同交付人工评审。

#### 场景：评审者对比已完成的变更
- **当** 实施验证完成
- **则** 评审者收到图 9、图 41 和图 69 的基线与更新成对截图，且两者可在一致的截图条件下比较
