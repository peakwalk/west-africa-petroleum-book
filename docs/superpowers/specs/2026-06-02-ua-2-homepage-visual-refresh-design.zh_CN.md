# UA-2 首页视觉升级设计

**日期：** 2026-06-02

**对应任务：** `UA-2` Refresh Upstream Atlas Homepage Visual Design and Branding

## 目标

在不改变当前静态站点和 mdBook 内容生产链路的前提下，重构 Upstream Atlas 首页的视觉系统、信息层级和模块编排，使其从“在线书籍入口”转为“西非石油情报平台入口”。

## 背景

当前首页已经具备可用的信息结构和基础品牌资产，但整体观感仍更接近 documentation site 或 online textbook：

- 标题与导航的字体语气偏学术，不够平台化
- 配色尚未对齐 `UA-2` 票面要求
- Hero 区更像图书封面导语，而不是情报平台入口
- 缺少体现未来能力方向的模块，例如平台能力卡和国家情报覆盖区
- 顶部导航仍偏向站内浏览，而非产品定位表达

`UA-2` 的核心不是单纯“换皮”，而是借首页建立以下认知：

- 平台具备权威性和行业可信度
- 产品能力不仅是阅读内容，还包括研究、监测和未来 AI intelligence
- 网站将向 premium West African petroleum intelligence platform 方向演进

## 范围

本次包含：

- 首页 `index.html` 的信息架构和模块重排
- 首页视觉 token、字体、颜色和卡片语言重建
- Hero 区的视觉升级
- 新增平台能力卡区
- 新增 Country Intelligence 区
- 顶部导航与 CTA 的重构
- 首页响应式行为调整
- 与首页改动对应的渲染测试更新

本次不包含：

- `/book/` 阅读器壳层改造
- `chapters/` 页面改造
- 引入 React、Vite 或其他运行时
- 新建真实国家详情页或资源详情页
- 章节内容、Markdown、mdBook 主题逻辑变更

## 第一性原理约束

### 1. 首页首先传递定位，而不是穷尽内容

首屏需要回答三个问题：

- 这是什么平台
- 为什么值得信任
- 用户下一步应该做什么

因此 Hero 必须强化标题层级、解释文案和 CTA，而不是继续采用偏“图书简介”的语气。

### 2. 高级感来自系统性，不来自复杂技术

高级感应由以下因素共同建立：

- 严格的配色 token
- 明确的标题/正文双字体系统
- 稳定的卡片与按钮语言
- 足够的留白和节奏
- 低噪声但有行业语义的背景装饰

本次不依赖额外前端框架，也不依赖重动画。

### 3. “未来 AI 能力”要通过结构预埋而非空泛口号表达

首页需要出现明确的平台能力层级：

- Research
- Industry Monitoring
- Intelligence

其中 `Intelligence` 保留 `Coming Soon` 标识，用来建立路线图感，但不虚构当前已上线能力。

### 4. 性能和维护性是硬约束

实现必须继续保持：

- 静态 HTML + CSS + 图片资产
- 构建命令不变
- 页面加载轻量
- 生成结果可被现有脚本验证

## 设计决策

### 1. 首页单独收敛到 UA-2 视觉方向

现有站点已有 landing redesign 与 book reader redesign 文档。对于首页，本次以 `UA-2` 作为最高设计约束；`/book/` 阅读器继续保持既有阅读方向，不跟随本次任务调整。

### 2. 字体系统切换为 Manrope + Inter

- `Manrope`：用于 `H1-H4`、导航、按钮、卡片标题
- `Inter`：用于正文、辅助说明、列表和元信息

这样可以让首页语气从“学术阅读”转为“现代平台”。

### 3. 颜色 token 严格对齐票面

- Primary: `#0B1F33`
- Secondary: `#D88A1D`
- Supporting Accent: `#1F5E7A`
- Background: `#F7F8F9`

所有按钮、标签、卡片描边、悬浮态和大区背景都从这四组 token 派生，避免继续混用上一版蓝橙体系。

### 4. Hero 背景采用“图片 + 情报纹理”双层结构

保留现有 hero 图片资产作为真实行业语境，同时叠加低透明度的情报纹理：

- licence block / grid 感的线框
- seismic / contour 感的重复线条

透明度控制在 5% 到 10%，不牺牲可读性。

### 5. 导航改成“平台入口导航”

导航调整为：

- `Home`
- `Countries`
- `Chapters`
- `Resources`
- `About`

右侧独立 CTA：

- `Start Reading`

`Countries` 与 `Resources` 默认落到首页锚点，保证链接真实可用。

### 6. 新增两个平台化区块

#### Platform Positioning

Hero 下紧接三张能力卡：

- Research
- Industry Monitoring
- Intelligence (`Coming Soon`)

#### Country Intelligence

展示八个国家卡片：

- Nigeria
- Ghana
- Angola
- Senegal
- Mauritania
- Namibia
- Côte d’Ivoire
- Equatorial Guinea

MVP 阶段只实现占位卡，但卡片结构要预留未来字段位。

## 信息架构

首页从上到下调整为：

1. 吸顶导航
2. Hero
3. Platform Positioning / Feature Cards
4. About / Editorial framing
5. Country Intelligence
6. Audience
7. Resources / Chapter Preview
8. Author / Publication note
9. Footer

## 实施文件

- `index.html`
- `assets/css/landing.css`
- `scripts/test-site-render.sh`

## 风险与缓解

### 风险：与现有首页 redesign 文档方向存在偏差

缓解：

- 首页以 `UA-2` 为准
- 阅读器和章节页不纳入本次改动

### 风险：首页模块增加导致页面显得臃肿

缓解：

- 每个区块只保留一层主要目标
- 用清晰标题、短文案和一致卡片节奏控制密度

### 风险：字体与背景升级拖慢首屏

缓解：

- 仅新增 `Manrope`
- 不引入额外 JavaScript
- 背景纹理优先使用 CSS 渐变与轻量图层，不增加大体积位图

## 验收标准

- 首页标题、导航、按钮切换到 `Manrope`
- 首页正文使用 `Inter`
- 首页配色切换到 `UA-2` 票面 token
- Hero 明显更接近石油情报平台而非在线教材
- Hero 下出现三张平台能力卡
- 出现 Country Intelligence 区块
- 导航包含 `Countries`、`Chapters`、`Resources`、`About`，并保留右侧 `Start Reading` CTA
- 首页在桌面、平板、手机宽度下可用
- `npm run test:site` 和 `npm run build` 可通过
