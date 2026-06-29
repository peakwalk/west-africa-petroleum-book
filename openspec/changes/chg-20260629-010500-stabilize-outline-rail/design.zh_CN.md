## 背景

阅读器会为一小部分页面保留桌面端 outline rail 的宽度，即使这些页面有意隐藏或抑制可见的 outline 内容。该分类逻辑目前同时存在于 `theme/index.hbs` 和 `theme/custom.js` 中，因此只要路径增删不同步，启动阶段与 hydration 后阶段就可能分叉。阅读器还会在运行时动态生成 figure outline 项，这意味着仅查看静态 HTML，无法判断脚本执行后页面是否仍具有可见 outline 内容。

## 目标 / 非目标

**目标：**
- 为桌面端页面变体分类提供单一共享来源，并把结果直接写入生成后的 HTML。
- 增加一个基于运行时 outline 可见性的回归检查，而不是只看静态标记。
- 在不修改章节源内容的前提下，让 figure 注释逻辑对轻微 caption 格式漂移更稳健。

**非目标：**
- 不重构 figure 流水线为构建时直接输出规范 `<figure>` 标记。
- 不用新的元数据系统替换当前的 preserve-outline-rail 页面列表。
- 不修改章节文案，也不重平衡阅读器 CSS token。

## 决策

1. 新增共享模块 `scripts/shared/book-page-variants.mjs`，并让 `scripts/localize_reader_shell.mjs` 在每个生成后的书页上直接写入对应的 body class。
   - 这样可以彻底移除运行时页面分类器，同时保留一份权威的 preserve-outline-rail 路径表。
   - 备选方案：继续保留运行时 helper，只把启动阶段分类器缩小。否决原因：这样仍然会在生成 HTML 和 hydration 行为之间保留双份分类逻辑。
2. 保留显式 preserve-outline-rail 列表，并将其收口到共享模块中。
   - 这是最小且安全的修复，因为 `chapter-11-general-conclusion.html` 这种没有标题也没有 figure 的内容页，仍然需要显式例外。
   - 备选方案：完全依赖内容形态推导保留页面。否决原因：有些预期例外页本身没有运行时 outline 信号。
3. 在站点渲染测试里加入共享页面变体和 outline 计数逻辑的导入，而不是从 theme 源码里切出函数再执行。
   - 这样可以补上当前缺口，避免路径列表漂移或 caption 解析漂移在不报错的情况下改变布局，同时避免在 shell 里再抄一份算法。
   - 备选方案：只断言源码字符串。否决原因：源码断言无法证明生成后的书页仍然安全。
4. 增强 `annotateFigureCaptions()`，增加 alt 标签兜底：只有当图片 alt 像 `Figure N`，且紧随其后的段落足够短、看起来像 caption 时，才将其提升为 figure。
   - 这样可以覆盖退化的 figure 标记，同时避免把长篇正文误判为 caption。
5. 为 macOS 本地验证增加一个基于 localhost 的可选浏览器回放检查，并默认只跑少量哨兵页冒烟，同时保留显式触发的全量扫描。
   - 这样可以在不把每次本地验证都变成整本书 WebKit 巡检的前提下，为 figure/reference hydration 增加一层更接近真实浏览器的验证，同时让校验继续对齐页面的真实行为。
   - 备选方案：继续只通过 `file://` 探测构建产物，或者在校验器里覆盖 `requestAnimationFrame`。否决原因：文件协议会抑制或延后站点依赖的同源 sidebar 与 metadata 流程，而调度器覆盖会掩盖回放本应发现的时序问题。
6. 将 `readerRuntimeInitialized` 的设置延后到核心启动序列完成之后，并在同步初始化失败时允许一次安全重试；同时把 sidebar observer 改成限流后在投影导航稳定时断开。
   - 这样可以避免页面在半初始化状态下被错误标记成“已完成”，也可以防止 sidebar 细碎变更持续触发高成本的运行时 hydration。
   - 备选方案：继续保留提前置位的初始化标记，以及贯穿整页生命周期的 whole-sidebar observer。否决原因：部分失败仍然不可恢复，稳态 DOM 抖动也会持续支付不必要的运行时成本。

## 风险 / 权衡

- [风险] 构建期 body class 注入可能与 preserve-outline-rail 预期发生漂移。
  → 缓解：把页面变体表放进同一个共享脚本模块，并在站点验证里断言生成页面的 body class。
- [风险] 运行时 outline 模拟与浏览器行为出现漂移。
  → 缓解：让检查严格对齐阅读器当前使用的信号：标题、figures、tables、formulas，以及 figure 兜底所依赖的顶层块相邻关系。
- [风险] 基于 alt 的 figure 兜底可能把图片后的普通段落误判成 caption。
  → 缓解：要求图片 alt 必须符合 `Figure N`，且相邻段落必须足够短并且不像正文句子。
- [风险] 浏览器级检查可能变得不稳定，或者过于依赖本机环境。
  → 缓解：只在具备 macOS `swift`/`WebKit` 的环境下运行，通过 localhost 而不是 `file://` 提供 `public/`，由 `theme/custom.js` 暴露仓库自有的 hydration-ready 状态信号，默认跑少量哨兵页冒烟并保留全量扫描开关，并从共享页面变体模块导出 preserve-outline 预期，避免在 Swift 里重复维护规则。
- [风险] reader runtime 启动可能在部分 DOM 已变更后失败，或者 sidebar 变更触发重复的整页刷新。
  → 缓解：只有在核心启动序列成功后才标记初始化完成，对同步启动失败只允许一次有界重试，并在投影导航稳定后断开已限流的 sidebar observer。
