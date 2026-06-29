## ADDED Requirements

### Requirement: Homepage shell MUST orient first-time visitors around the approved primary actions
公共首页 SHALL 提供一个共享 shell，让用户一进入就能理解产品定位，并看到已经批准的主动作：`Countries`、`Chapters`、`Search` 和 `Contact`。已经过时的顶层 `Resources` 与 `About` 入口 MUST NOT 继续保留在首页主导航中。

#### Scenario: Homepage navigation exposes the approved primary actions
- **WHEN** 用户打开公共首页
- **THEN** 顶层导航包含 `Countries`、`Chapters`、`Search` 和 `Contact` 的直接动作
- **THEN** `Countries`、`Chapters` 与 `Search` 会分别定位到国家发现、主题发现和图书搜索对应的首页区块
- **THEN** 主导航中不再包含旧的 `Resources` 或 `About` 项

#### Scenario: Hero orients the user toward the current edition
- **WHEN** 用户进入英文首页
- **THEN** hero 说明 Upstream Atlas 作为西非石油独立参考入口的定位
- **THEN** 它包含一个清晰的 current-edition 入口，并进入现有图书面

### Requirement: Homepage MUST provide country-led discovery for all covered West African countries
首页 SHALL 把 `Coverage Across West Africa` 作为最主要的探索面。它 SHALL 用统一规格的卡片列出 16 个覆盖国家，并在每张卡片中包含一致的尺寸、状态标识、ministry 元数据、national oil company 元数据、规模指标，以及进入 chapter 3 对应国家小节的 CTA。

#### Scenario: Country cards provide complete country entry points
- **WHEN** 英文首页渲染国家发现区块
- **THEN** 其中包含 16 个覆盖国家各自的一张卡片
- **THEN** 每张卡片都展示状态、ministry/NOC 信息、规模指标和国家 CTA

#### Scenario: Country cards deep-link into the book
- **WHEN** 用户点击某个国家 CTA，例如 Nigeria
- **THEN** 目标会进入现有图书输出中 chapter 3 对应国家的锚点位置

### Requirement: Homepage MUST provide a geographic map as a secondary country-navigation aid
首页 SHALL 提供一张可点击的西非政治地图，作为国家导航的地理辅助入口，并指向与国家卡片完全一致的国家目标。地图 MUST 只是国家卡片网格的补充，MUST NOT 引入第二套相互冲突的国家路由模型。

#### Scenario: Map routes to the same destination as the country card
- **WHEN** 用户在西非地图上选择某个国家
- **THEN** 最终目标与该国家卡片 CTA 使用的目标完全一致

#### Scenario: Map remains supplemental to the card grid
- **WHEN** 首页在桌面端或移动端渲染
- **THEN** 即使用户完全不使用地图，国家卡片网格仍然提供完整的国家发现路径

### Requirement: Homepage MUST provide topic discovery that does not overlap with country discovery
首页 SHALL 用 `Browse by Topic` 替换 `Explore the Reference Library`，并把这个区块专门用于进入现有图书章节中的精选主题目标。主题发现 MUST 与国家发现、搜索这两类能力保持职责分离。

#### Scenario: Browse by Topic points to approved chapter destinations
- **WHEN** 首页渲染主题发现区块
- **THEN** 区块标题为 `Browse by Topic`
- **THEN** 每张主题卡片都链接到现有图书中的已批准 canonical 章节目标

#### Scenario: Topic browsing remains distinct from country browsing
- **WHEN** 用户扫描首页结构
- **THEN** 国家入口出现在国家发现区块
- **THEN** 主题章节入口出现在 `Browse by Topic`
- **THEN** 这两个模块不会重复承担同一种主要职责

### Requirement: Homepage MUST provide a book-only search entry
首页 SHALL 包含一个 `Search Upstream Atlas` 区块，把用户导入现有在线图书搜索面。这个区块 MUST 清楚说明搜索范围仅限于图书内容，且在本阶段 MUST NOT 暗示存在一套独立的全站搜索后端。

#### Scenario: Search section routes into the existing book search experience
- **WHEN** 用户使用首页搜索入口
- **THEN** 流程进入现有在线图书的 mdBook 搜索面
- **THEN** 区块文案明确说明搜索范围是图书内容

### Requirement: Homepage MUST communicate freshness, edition state, and contact paths
首页 SHALL 用 `Latest Updates` 替换低信号的 authors 模块，保留 `Current Edition`，简化 `Future Development`，并增强 footer coverage/contact 信息。共享 shell 中的搜索与联系动作 SHALL 在英文和法文构建下都保持 locale-safe。

#### Scenario: Latest Updates replaces the authors module
- **WHEN** 首页渲染可信度与更新区块
- **THEN** 页面展示的是 `Latest Updates`，而不是 authors 区块
- **THEN** 它向用户传达最近的版本或数据更新信号

#### Scenario: Contact action is directly available and locale-safe
- **WHEN** 用户从英文或法文首页触发 contact 动作
- **THEN** 动作会以已批准的收件人和主题行为打开 Upstream Atlas 当前维护的联系目标
- **THEN** 共享 shell 不会把用户带到损坏链接或语言不合适的目标
