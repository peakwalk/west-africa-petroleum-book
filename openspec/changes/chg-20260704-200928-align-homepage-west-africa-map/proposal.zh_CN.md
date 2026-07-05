## Why

当前首页的地图概览模块与已批准参考图偏差很大。它仍然使用抽象陆块、过大的编辑式标题，以及橙色 CTA，因此这一块已经不像一个“西非政治地图入口”。

用户已经提供了明确的目标图。本次需要补一个范围很小、归仓库管理的变更，把首页地图面板对齐到该西海岸参考构图，同时保留现有国家分析页面的跳转契约。

后续视觉复核也表明，首页目前仍混用了多套断点约定（`700 / 900 / 1100 / 1200 / 1201`）以及流体桌面字号。这会让 1440px 及以上的桌面构图继续漂移，地图概览标题尤为明显。首页需要一套明确的响应式区间模型，让 phone、pad、small desktop 和 locked desktop 的行为可预测。

同一次复核还暴露了主要国家卡片入口上的兼容性问题：首页国旗仍依赖外部 SVG sprite 的 `<use>` 引用，在一些独立静态预览或嵌入式渲染器里会直接消失。首页需要把共享国旗 sprite 内联一次，确保卡片在这些场景下也能稳定显示。

## What Changes

- 用与批准参考图一致的西非西海岸政治地图面板替换当前抽象地图，包括佛得角插图圆框和沿海岸线展开的大陆底图。
- 调整地图概览区左侧文案、间距、字体和 CTA 处理，使其贴近参考图的紧凑呈现。
- 保留现有国家深链：虽然可见地图面板会更换，但热点点击仍然指向与国家卡片相同的目标页面。
- 将首页断点整理为四个明确区间：`0-767` phone、`768-1023` pad、`1024-1439` small desktop、`1440+` desktop locked。
- 在首页输出里内联共享国旗 sprite，并把国家卡片国旗切换为本地片段引用，而不是外部 sprite URL。
- 补齐或更新与该资源、标记结构和首页输出相关的最小构建/测试断言。

## Capabilities

### New Capabilities
- `homepage-map-reference-alignment`：首页地图概览模块以批准的西海岸政治地图参考样式渲染，同时保留可访问的国家热点入口，跳转到现有书籍内容。

### Modified Capabilities
- None.

## Impact

- 受影响的生成源码：`scripts/shared/homepage-content.mjs`
- 受影响的首页样式：`assets/css/landing.discovery.css`、`assets/css/landing.homepage-v2.css`、`assets/css/landing.header.css`、`assets/css/landing.responsive-tablet.css`、`assets/css/landing.responsive-mobile.css`
- 受影响的视觉资源：`assets/images/*`、`assets/icons/*`
- 重建后受影响的产物：`index.html`、`public/index.html` 以及本地化首页变体
- 受影响的验证：`scripts/test-site-render.sh`、`tests/test_homepage_country_flags.py`，以及一张本地视觉对比截图
