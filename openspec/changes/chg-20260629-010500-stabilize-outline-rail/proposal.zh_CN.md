## 为什么

桌面端阅读器目前在两个位置分别决定是否保留 outline rail，占位逻辑已经导致过 `chapter-11-general-conclusion.html` 与同类章节出现不同左边距。同一区域还依赖脆弱的运行时 figure 识别，因此只要 caption 格式轻微漂移，就可能静默丢失 outline 内容并再次引入同类布局回归。

## 变更内容

- 收口书页变体分类逻辑，让生成后的书页直接带上正确的 `preserveOutlineRail` 相关 body class，而不是依赖运行时分类器。
- 增加站点渲染回归检查，模拟运行时 outline 可见性；如果真实章节页会落到“空 outline 且未显式保留 rail”的状态，则直接失败。
- 增强运行时 figure caption 注释逻辑；当显式 `Figure N ...` 文本缺失或部分退化时，仍可根据图片 alt 标签和紧邻的短 caption 段落生成 figure card。

## 能力

### 新增能力
- `reader-outline-rail-stability`：在启动、hydration 和运行时 figure 注释变化下，保持桌面端阅读器正文列对齐稳定。

### 修改能力
- 无。

## 影响

- 影响代码：`theme/index.hbs`、`theme/custom.js`、`scripts/localize_reader_shell.mjs`、新的共享脚本 helper，以及 `scripts/test-site-render.sh`
- 验证方式：主题/源码断言，以及 `npm run build:site` 和 `npm run test:site`
- 风险面：桌面端阅读器布局、运行时 outline 可见性，以及英法文章节的 figure caption 解析
