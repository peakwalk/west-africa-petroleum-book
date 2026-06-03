# UA-3 首页图标系统设计

**日期：** 2026-06-03

**对应任务：** `UA-3` Homepage Iconography Design & Implementation

## 目标

在不改变当前静态站点与 mdBook 生成链路的前提下，为 Upstream Atlas 首页建立一套统一、可复用、可扩展的 SVG 图标系统，并将其接入首页核心入口模块，使首页更清晰地呈现为 premium West African petroleum intelligence platform。

## 背景

`UA-2` 已经完成首页的结构升级与视觉基调重建，当前首页已经具备：

- Hero 区与平台定位文案
- Platform Intelligence 三张能力卡
- Country Intelligence 国家情报卡片
- Audience、Resources 与章节预览区
- 统一的 header / footer shell

但首页仍缺少一套正式的图标系统：

- Platform Intelligence 卡片没有图标支撑语义识别
- Country Intelligence 的 signal 项只有文字，没有分类图标
- Header CTA、mobile menu 仍未进入统一 SVG 图标语言
- Audience 区保留的是另一套实心 inline SVG，和预期的线性 / duotone 风格不一致
- 仓库中不存在可复用的 homepage icon library

`UA-3` 的核心不是“添加一些图标”，而是为首页补上语义视觉层，使用户更快理解平台能力、国家情报维度和关键操作入口。

## 范围

本次包含：

- 建立一套首页专用 SVG 图标资产
- 产出独立 SVG 文件与一个可引用的 sprite 文件
- 为 Platform Intelligence 三张能力卡接入图标
- 为 Country Intelligence signal 分类接入图标
- 为 header CTA 与 mobile navigation 接入图标
- 统一 Audience 区现有图标语言，避免首页出现两套风格并存
- 补充与图标系统相关的样式和回归测试

本次不包含：

- 自动将用户提供的整张参考图直接矢量化为生产资产
- 一次性建设完整的“全站图标库”
- `book/` 阅读器图标重构
- `chapters/` 页面内容图标重构
- Future Expansion 与 Upstream Operations 的全量示例图标一次性全部落地到页面
- 引入新前端框架、图标库运行时或构建工具

## 第一性原理约束

### 1. 图标的职责是降低识别成本，而不是增加装饰密度

图标必须帮助用户更快识别：

- 这张卡属于什么能力
- 这条国家情报 signal 属于什么维度
- 这个按钮会触发什么动作

如果图标不能缩短理解路径，它就只是噪音。

### 2. 统一性比数量更重要

首页图标系统必须统一以下要素：

- 描边粗细
- 端点与转角风格
- 主色与强调色规则
- 基础画板尺寸
- 图标与文案的间距节奏

不能出现平台卡是细线双色图标、Audience 区是实心图标、CTA 又是第三种图标语言的情况。

### 3. 资产可复用比一次性内联更重要

`UA-3` 明确要求为未来扩展打基础，因此实现必须产出：

- 可单独复用的 SVG 文件
- 一个供页面引用的 sprite 文件

而不是只把几段随机 inline SVG 塞进首页。

### 4. 首页是平台入口，不是图标展示页

图标密度必须克制：

- Platform Intelligence 卡片可以使用较大的主图标
- Country Intelligence 只在 signal 级别使用小图标
- 导航动作图标只用于关键动作，不给所有导航项都配图标

### 5. 性能与维护仍是硬约束

实现必须保持：

- 静态 HTML + CSS + SVG 资产
- 构建命令不变
- 无额外 JavaScript 图标运行时
- 生成结果可被现有脚本验证

## 参考图的使用方式

用户提供的图标板将被定义为 `style baseline`，用途是：

- 约束图标语义方向
- 约束蓝橙双色风格
- 约束 clean line / restrained duotone 的视觉语言

该参考图**不会**被直接当作生产资产使用，也不会做“整图自动矢量化后直接上线”。

原因：

- 截图不是原始图标源文件
- 自动矢量化会得到脏路径和不稳定线宽
- 不利于维护与后续扩展

因此本次采用“参考风格，重新生成干净 SVG”的路线。

## 设计决策

### 1. 采用“最小可用图标库 + sprite + 独立源文件”的资产策略

新增一个首页图标资产目录，保存每个独立 SVG；同时额外维护一个 `homepage-sprite.svg` 供页面使用。

这样可以同时满足：

- `UA-3` 对 individual SVG assets 的要求
- 页面对统一引用与缓存的需求
- 后续对单图标扩展和替换的需求

### 2. 采用 24x24 基础网格和统一线宽

统一使用：

- 设计网格：`24x24`
- 统一描边：`2`
- 圆角端点、圆角转折

推荐输出展示尺寸：

- `24px`
- `32px`
- `48px`
- `64px`

### 3. 保持主色 + 强调色的克制双色规则

颜色遵循：

- Primary icon color: `#1F5E7A`
- Accent color: `#D88A1D`
- Optional dark variant: `#0B1F33`

约束：

- 主轮廓以 `#1F5E7A` 为主
- 强调色只用于少量 semantic highlight
- 不使用渐变
- 不使用复杂阴影
- 深色底自动降级为单色浅色或白色版本

### 4. 首页首轮只建设真正影响认知的核心图标

首轮正式落地图标分为三组：

#### 平台定位图标

- `research`
- `industry-monitoring`
- `intelligence`

#### 国家情报分类图标

- `production`
- `exploration`
- `fiscal`
- `regulation`

#### 导航与 CTA 图标

- `start-reading`
- `menu`
- `close`

此外，为保持首页图标语言一致，本次同步重建 Audience 区图标：

- `audience-research`
- `audience-policy`
- `audience-operators`

首轮共计 `13` 个生产级 SVG 图标。

### 5. Contact 图标不单独扩 scope，但需对齐风格

当前 header 的 contact icon 已是线性 SVG。它不单独进入首轮图标库计数，但样式层必须与新图标系统对齐：

- stroke 粗细一致
- 色彩 token 一致
- hover 态与按钮图标协调

### 6. Country Intelligence 先做“语义归一”，再做图标映射

国家卡中的 signal 文案并不完全一致，例如：

- Production / Gas / Supply
- Exploration / Licensing / Blocks / Offshore / Projects
- Fiscal / Revenue / Commercial
- Regulation / Governance / Policy / Operations / Infrastructure

本次不为每一个 signal label 单独设计图标，而是先映射到四个受控分类：

- `production`
- `exploration`
- `fiscal`
- `regulation`

正式映射规则：

- `Production`、`Gas`、`Supply` -> `production`
- `Exploration`、`Licensing`、`Blocks`、`Offshore`、`Projects` -> `exploration`
- `Fiscal`、`Revenue`、`Commercial` -> `fiscal`
- `Regulation`、`Governance`、`Policy`、`Operations`、`Infrastructure` -> `regulation`

这样可以避免图标系统无限膨胀。

### 7. `Start Reading` 只保留一种主图标

参考图中给出了箭头、书、本指南针三个备选方向。

本次明确选用：

- `Start Reading` -> 箭头语义

原因：

- 动作性最强
- 最符合 CTA 预期
- 比书或指南针更少“内容站”或“地图产品”误导

### 8. 不给每张国家卡放大型占位图标

参考图中存在“非洲地图占位图标”的方案。

本次不在每张国家卡上放大型占位图标，原因：

- 国家卡已经信息密度较高
- 大图标会削弱 country signal grid 的权重
- Country Intelligence 的核心是维度结构，而不是装饰性占位图

如果后续需要 empty state 或默认图，可在二期引入。

## 信息架构落点

### 1. Platform Intelligence

在每张 feature card 顶部加入一个 `48px` 主图标：

- Research：政府 / 文件检索语义
- Industry Monitoring：海上平台 / rig / 监测语义
- Intelligence：AI / network nodes 语义

`Coming Soon` 继续使用现有 badge 系统，不写死在图标本体中。

### 2. Country Intelligence

在每条 signal item 中加入一个小型分类图标，而不是新增整卡大图标：

- 渲染尺寸固定为 `18px`
- 图标与 label 左对齐
- 保持 signal 卡片的表格感与节奏感

### 3. Header 与 CTA

接入：

- `Start Reading` 按钮图标
- mobile `Menu` 图标
- mobile `Close` 图标

保留文字，不允许纯图标按钮替代现有文案。

### 4. Audience

当前 Audience 使用的是另一套实心图标。本次统一替换为同一语言体系下的线性 / 克制双色图标，避免首页视觉语言断裂。

## 文件结构

新增：

- `assets/icons/homepage/icon-research.svg`
- `assets/icons/homepage/icon-industry-monitoring.svg`
- `assets/icons/homepage/icon-intelligence.svg`
- `assets/icons/homepage/icon-production.svg`
- `assets/icons/homepage/icon-exploration.svg`
- `assets/icons/homepage/icon-fiscal.svg`
- `assets/icons/homepage/icon-regulation.svg`
- `assets/icons/homepage/icon-start-reading.svg`
- `assets/icons/homepage/icon-menu.svg`
- `assets/icons/homepage/icon-close.svg`
- `assets/icons/homepage/icon-audience-research.svg`
- `assets/icons/homepage/icon-audience-policy.svg`
- `assets/icons/homepage/icon-audience-operators.svg`
- `assets/icons/homepage-sprite.svg`

修改：

- `src/index-main.html`
- `scripts/shared/landing-shell.mjs`
- `assets/css/landing.css`
- `scripts/test-site-render.sh`

## 实现策略

### 1. 页面使用 sprite，资产保留单文件源

页面层优先引用 `homepage-sprite.svg`，例如：

- feature cards
- country signal icons
- CTA icons

同时保留独立 SVG 文件作为源资产与后续复用资产。

### 2. 不引入新构建步骤

本次不增加新的图标构建脚本或依赖。

原因：

- 当前站点以静态生成和低复杂度维护为目标
- 图标数量仍处于可以人工维护的规模
- 为 13 个图标引入额外 toolchain 不划算

### 3. Header 图标路径必须兼容首页、chapters、legal 页面

由于 header 来自 `scripts/shared/landing-shell.mjs`，图标引用路径需要通过现有 `basePath / logoBasePath` 机制解析，保证：

- 首页路径正确
- `chapters/` 页路径正确
- legal 页路径正确

### 4. 统一图标样式 API

在 CSS 中增加统一图标类，例如：

- `.ua-icon`
- `.ua-icon--sm`
- `.ua-icon--md`
- `.ua-icon--lg`
- `.ua-icon-slot`

统一控制：

- 尺寸
- 对齐
- `currentColor`
- 深浅底适配
- hover / focus 响应

## 可访问性

- 装饰性图标统一 `aria-hidden="true"`
- 按钮与链接必须保留文字标签
- 不通过图标单独传递关键状态
- `Coming Soon`、`Available now` 等状态继续保留文字 badge

## 风险与缓解

### 风险：图标范围膨胀成整站系统改造

缓解：

- 明确本次只做首页核心图标
- 不把 Future Expansion 全量示例拉入实现范围

### 风险：国家 signal label 过散导致图标无法统一

缓解：

- 先建立 label -> category 的受控映射
- 严格限制到四类图标

### 风险：首页出现两套图标语言

缓解：

- Audience 区同步纳入统一风格
- Contact icon 至少在样式上对齐

### 风险：过多图标导致页面显得拥挤

缓解：

- 仅 feature card 使用大图标
- country card 仅使用小 signal 图标
- 导航不为每个链接配图标

### 风险：sprite 路径在不同页面失效

缓解：

- Header 图标路径统一经 shell helper 生成
- 在 `test:site` 中加入不同页面的路径断言

## 验收标准

### 资产层

- 首轮 `13` 个图标均以干净 SVG 文件交付
- 存在一个 `homepage-sprite.svg`
- 命名规范一致

### 页面层

- Platform Intelligence 三张能力卡显示正式图标
- Country Intelligence signal 项显示统一分类图标
- `Start Reading`、`Menu`、`Close` 显示正式 SVG
- Audience 区图标已统一到同一视觉语言

### 视觉层

- 图标线宽、转角、主色、强调色规则一致
- 浅底与深底都清晰可读
- 移动端不出现拥挤、错位或断行问题

### 工程层

- 不引入新前端框架和图标运行时
- `npm run test:site` 可通过
- `npm run build` 可通过
- 图标路径在首页、chapters、legal 页面均正确

## 实施顺序建议

1. 生成与整理 SVG 资产
2. 产出 `homepage-sprite.svg`
3. 接入 `src/index-main.html` 的 feature cards、country signals、audience
4. 接入 `scripts/shared/landing-shell.mjs` 的 CTA / mobile nav
5. 补充 `assets/css/landing.css` 图标系统样式
6. 更新 `scripts/test-site-render.sh`
7. 跑 `npm run test:site`
8. 跑 `npm run build`

## 最终决策

`UA-3` 将采用“参考图作为风格基线，重新生成生产级 SVG 图标”的路线，而不是直接对截图做自动矢量化。

首轮范围收敛到首页核心图标系统，并明确交付：

- 独立 SVG 图标文件
- 一个 sprite 文件
- 首页关键模块的接入
- 与之匹配的样式与测试

这样既满足当前 Jira 需求，也为后续图标扩展留出清晰的资产基础。
