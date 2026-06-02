# UA-6 公开站点 Footer 设计说明

**日期：** 2026-06-02

**目标**

为 Upstream Atlas 的公开站点入口页建立统一、专业、可复用的 footer，同时明确 **不在 mdBook 阅读页中加入 footer**，以保护书页阅读体验。

## 背景

`UA-6` 原始 Jira 描述希望首页与书页都出现统一 footer，但经产品边界确认，本次实现范围调整为：

- 首页 `index.html` 增加完整 footer
- 章节库 `chapters/index.html` 增加完整 footer
- 站点法律页增加真实落地页并使用同一 footer
- mdBook 章节正文页、子章节页、打印页 **不增加 footer**

当前仓库已经存在两个独立壳层：

- 公开站点壳层：`scripts/shared/landing-shell.mjs`
- mdBook 阅读器壳层：`theme/index.hbs`

如果把 footer 放进 mdBook 模板，会把营销/法律导航带入阅读器，破坏当前“纯阅读”布局。因此本次只升级公开站点壳层。

## 范围

### In scope

- 重构 landing shell footer 为完整四列结构
- 让首页与章节库页共享同一 footer 渲染源
- 增加 `Terms of Use`、`Privacy Policy`、`Cookie Policy` 三个真实站内页面
- 让 footer 法律链接落到站点根路径 canonical URL
- 让 footer 在桌面四列、移动端堆叠
- 让 “Latest Updates / Industry News” 作为非死链的 future items 呈现
- 扩充静态站点测试，锁定 footer 合同与 “mdBook 不加 footer” 的边界

### Out of scope

- 在 `theme/index.hbs` 或 `theme/custom.css` 中加入任何 footer
- 修改 mdBook toolbar、章节导航、搜索、阅读布局
- 增加 contact form
- 增加 newsletter、RSS、动态更新流
- 增加平台侧 footer 或平台法律页

## 第一性原理

footer 的职责不是“页面装饰”，而是公开入口页底部的信任收口。它需要在用户完成浏览后稳定提供四类信息：

1. 品牌说明：这个站点是什么、为什么可信
2. 关键导航：用户下一步能去哪里
3. 合规入口：法律条款在哪里
4. 联系方式：用户如何发起反馈与咨询

mdBook 章节页的主要任务则是连续阅读，不是营销导航。把公开站点 footer 强塞进阅读器，会引入额外滚动长度、视觉终点噪音和信息层混杂。因此本次采用“公开站点有 footer、阅读器无 footer”的双壳层策略。

## 信息架构

### Column 1: Upstream Atlas

- 标题：`Upstream Atlas`
- 文案：`Practical insights into the technical, commercial, fiscal, regulatory, and governance aspects of the West African oil and gas industry.`

### Column 2: Explore

- `Home`
- `About`
- `Countries`
- `Book Contents`
- `Contact`

### Column 3: Resources

- `Latest Updates`（future item，不跳转）
- `Industry News`（future item，不跳转）
- `Terms of Use`
- `Privacy Policy`
- `Cookie Policy`

### Column 4: Contact Us

- 标签：`Email`
- 链接：`mailto:matt@operatorassetexchange.com`

### Bottom bar

- `© 2026 Upstream Atlas. All Rights Reserved.`
- 可选副标：`West Africa Oil & Gas Intelligence`

## URL 规则

沿用历史任务 `OAE-41` 的 canonical 路径，不再发明新命名：

- `/terms-of-use.html`
- `/privacy-policy.html`
- `/cookie-policy.html`

这些页面属于 **website legal group**，相互之间只在同组内互链。

## 法律页策略

仓库当前没有批准后的法律正文源文件，因此本次在代码层建立“真实页面 + 极简 legal shell + 同组互链 + 占位状态说明”的交付面：

- 顶部小 logo，点击回首页
- 标题
- 状态说明
- 最后更新时间
- 三个 website legal links
- 联系邮箱
- 占位说明内容

如果后续拿到批准正文，只替换正文内容源，不改 footer 和 legal shell 结构。

## 架构设计

### 1. Footer 渲染源集中化

在 `scripts/shared/landing-shell.mjs` 中集中管理：

- 公共导航链接
- 法律链接路径
- 邮箱目标
- footer 栏目配置

这样首页和章节库不会产生两份 footer 文案。

### 2. Landing 样式单独演进

在 `assets/css/landing.css` 中把当前简化 footer 升级为：

- 桌面四列网格
- 平板两列
- 手机单列
- 深色背景与清晰分隔
- 对链接、future item、邮箱项分别定义视觉状态

### 3. Legal 页静态生成

新增 `scripts/generate-legal-pages.mjs`，从 `src/legal/*.json` 或等价结构生成：

- `terms-of-use.html`
- `privacy-policy.html`
- `cookie-policy.html`

法律页 head、body、互链规则、logo 返回路径在同一脚本中生成，避免手写三份 HTML。

### 4. Placeholder 优先于 404 与未批准正文

在没有批准 legal text 的前提下，canonical legal URL 应先发布为 **200 的占位页**，而不是：

- `404`
- 空白页
- 工程侧自行撰写的正式政策文本

这样做的原因是：

- 链接语义成立，用户点击法律入口时会进入真实页面
- 风险可控，不会发布未经批准的正式法务文本
- canonical URL 先稳定下来，未来替换为正式正文时无需改 footer 和外链

### 5. mdBook 显式排除

`theme/index.hbs` 和 `theme/custom.css` 不作 footer 相关变更。测试也会显式断言 mdBook 输出中没有公开站点 footer 标记。

## 风险与缓解

- 风险：`UA-6` 原始 Jira 文字包含 book pages footer。
  缓解：本次实现以用户确认的范围调整为准，并在实现说明中明确 “mdBook excluded intentionally”。

- 风险：法律页批准正文尚未进入仓库。
  缓解：先落 legal shell、真实 URL 和占位说明；正式正文待批准后替换内容源。

- 风险：首页和章节库页在 future items 上出现死链接。
  缓解：future items 用非链接元素渲染，并加 `Coming soon` 辅助文案。

## 验收标准

- 首页底部出现完整四列 footer
- `chapters/index.html` 底部出现同一 footer
- footer 中 `Terms / Privacy / Cookie` 指向真实站内页面
- footer 中邮箱为 `mailto:matt@operatorassetexchange.com`
- 三个法律页均存在，且仅互链到 website legal group
- 三个法律页返回 `200`，且显示“待发布/待批准”的占位状态说明
- `npm run test:site` 通过
- `public/book/index.html` 与任一 `public/book/chapters/*.html` 中不出现 landing footer 标记
