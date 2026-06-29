## Why

当前首页仍然沿用较旧的信息组织方式，把定位说明、章节入口、国家入口和泛化资源入口混在一起，导致首次访问者很难快速回答几个最基本的问题：Upstream Atlas 是什么、覆盖哪些地理范围、如何按国家进入、如何按主题进入、如何搜索整本书，以及内容是否最新。

`resources/version2/` 里的 UA-11 Version 2 材料已经把首页目标重新定义得很清楚：要把 Upstream Atlas 建成西非石油领域最值得信任的独立参考入口，优先追求清晰、可信、快速导航和长期可扩展，而不是继续堆叠旧版模块。要在这个 repo 里稳妥落地这件事，需要先把首页重做写成 repo 自己维护的 OpenSpec change，把信息架构、范围边界和分阶段落地方式说清楚，而不是直接做一次性的模板重写。

## What Changes

- 按照第一性原理把首页重构为 5 个互不重叠且合在一起完整覆盖的用户意图层：定位说明、国家发现、主题发现、书内搜索，以及更新/联系信号。
- 更新共享 landing shell：移除已经过时的 `Resources` 与 `About` 顶层入口，保留 `Countries` 与 `Chapters`，新增直接的 `Search` 与 `Contact` 动作，并确保 EN/FR 两个版本都能安全复用。
- 用 Version 2 的结构替换当前英文首页主体：新版 hero、`Coverage Across West Africa` 国家卡片区、可点击的西非政治地图、`Browse by Topic`、`Search Upstream Atlas`、`Latest Updates`、`Current Edition`、`Topics Covered`、`Future Development` 以及增强后的 footer coverage。
- 把首页依赖的国家元数据、国家深链、主题跳转、最新更新和 footer coverage 文案收敛到结构化内容源中，避免内容散落在模板和脚本里。
- 复用现有静态 mdBook 路由和搜索索引作为章节、主题和搜索的目标面；本阶段不引入新的后端、数据库或独立搜索服务。
- 第一阶段只完整重做英文首页主体；法文首页通过共享 shell 和路由更新保持兼容。完整法文主体改版明确不在本次 change 范围内。

## Capabilities

### New Capabilities
- `homepage-information-architecture`: 公共首页提供一套清晰、可扩展、且适配静态构建的信息架构，让用户可以按国家、按主题或按书内搜索进入 Upstream Atlas，同时强化可信度、更新感知和联系路径。

### Modified Capabilities
- None.

## Impact

- 预期受影响的 landing page 源文件包括 `editions/en/site/index-main.html` 与 `editions/fr/site/index-main.html`。
- 预期受影响的生成与共享 shell 代码包括 `scripts/generate-index-page.mjs` 与 `scripts/shared/landing-shell.mjs`。
- 预期受影响的展示样式包括 `assets/css/landing.css`。
- 预期受影响的验证包括 `scripts/test-site-render.sh` 以及定向的 site-render 断言。
- 现有 mdBook 路由和搜索产物仍然是最终落点；本次 change 不应新增运行时基础设施。
