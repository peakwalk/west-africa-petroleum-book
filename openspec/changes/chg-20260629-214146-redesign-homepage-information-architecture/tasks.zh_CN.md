## 1. Homepage content model and routing contract

- [x] 1.1 增加一份由 repo 自己维护的结构化首页内容源，覆盖国家元数据、国家路由、主题目标、最新更新、footer coverage 以及共享首页文案。
- [x] 1.2 统一首页路由 helper，让国家卡片、西非地图、主题卡片、搜索入口和联系动作都通过同一份可维护的真值源解析。

## 2. Shared shell and hero redesign

- [x] 2.1 更新共享 landing shell 和顶层导航，移除已经过时的 `Resources` 与 `About`，保留 `Countries` 与 `Chapters`，新增 `Search` 和 `Contact`，接好区块定位与联系动作，并保证两个 edition 下的 locale-safe 行为。
- [x] 2.2 在英文首页中实现新版 hero 和新的首页区块顺序，包括更新后的定位文案和 current-edition 入口。

## 3. Discovery surfaces and trust modules

- [x] 3.1 把 `Coverage Across West Africa` 实现为 16 张统一规格的国家卡片，包含状态、ministry/NOC 元数据、规模指标和 chapter 3 深链。
- [x] 3.2 实现一张可点击的西非政治地图，并让它指向与国家卡片完全一致的国家目标。
- [x] 3.3 用 Version 2 材料中已批准的主题目标，把 `Explore the Reference Library` 替换为 `Browse by Topic`。
- [x] 3.4 新增 `Search Upstream Atlas`，作为仅搜索图书的入口，并复用现有 mdBook 搜索面。
- [x] 3.5 用 `Latest Updates` 替换首页 authors 模块，保留 `Current Edition`，简化 `Future Development`，并增强 footer coverage/contact 信息。

## 4. Verification and phased rollout

- [x] 4.1 更新 site-render 断言和定向测试，覆盖新的共享 shell、区块顺序、国家目标、主题目标、搜索入口和联系动作。
- [x] 4.2 运行 `npm run build:site` 与 `npm run test:site`，然后人工检查代表性的英文和法文首页输出。
- [x] 4.3 确认英文首页交付完整的 Version 2 主体改版，同时法文首页仍然可用，且不存在共享 shell 链接损坏问题。
