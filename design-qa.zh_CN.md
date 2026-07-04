# Hero 参考图对齐 QA

- 源图路径：`/var/folders/y7/ll1_jx7s583dgv6g95hpbx1m0000gn/T/codex-clipboard-e3c67afa-9647-4f61-82d1-3cfaff1bb0b8.png`
- 衍生 Hero 背景图路径：`/Users/edison/workspace/peakwalk/scm/gitlab/africa-book/assets/images/upstream-atlas-hero-v6-soft-left.webp`
- 实现截图路径：`/Users/edison/workspace/peakwalk/scm/gitlab/africa-book/output/playwright/landing-hero-refmatch-2026-07-02-j.png`
- 视口：`1440x900` 桌面端
- 状态：首页默认首屏
- 全视图证据：`/Users/edison/workspace/peakwalk/scm/gitlab/africa-book/output/playwright/landing-hero-refmatch-2026-07-02-j.png`
- Hero 聚焦证据：`/Users/edison/workspace/peakwalk/scm/gitlab/africa-book/output/playwright/landing-hero-refmatch-focused-2026-07-02-j.png`

**发现**
- 针对这一轮，没有剩余可执行的 `P0` / `P1` / `P2` 级问题。Hero 左侧已经不再渲染为独立的深色竖条，而是改成了连续的深蓝渐变暗场，更接近参考图的视觉结构，同时没有牺牲正文可读性，也基本保住了当前平台群的尺度。

**开放问题**
- 无。

**实施清单**
- 保持这张 soft-left Hero 背景图不变，后续只调整遮罩强度和位置。
- 如果后续 hero 背景源、遮罩或构图方式再次变化，重新跑桌面端截图 QA。

**本轮补丁**
- 用一张 soft-left 双平台黄昏背景图替换掉之前带硬边的加宽资产，让左侧暗场来自平滑过渡，而不是来自近黑色扩展条。
- 把左侧 hero 遮罩改成更宽的径向深蓝渐变，让暗场从画布边缘自然漫进来，而不是读成一根竖向暗柱。
- 保留当前平台摄影方向和大致尺度，同时把左到右的色阶过渡调顺。
- 把 hero 背景 CSS 和站点渲染检查一并切到新的 soft-left 资产链路。

final result: passed
