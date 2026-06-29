## ADDED Requirements

### Requirement: Shared Page Variant Classification
阅读器必须从同一份共享来源推导桌面端页面变体标记，使启动阶段和 hydration 后阶段针对同一路径应用一致的 preserve-outline-rail 判定。

#### Scenario: Preserved rail page during boot and hydration
- **WHEN** 某个路径命中显式保留 outline rail 的页面
- **THEN** 初始启动逻辑和 hydration 后阅读器逻辑都必须将该页面标记为保留桌面端 outline rail

#### Scenario: Non-preserved chapter page during boot and hydration
- **WHEN** 某个路径未命中显式保留 outline rail 的页面
- **THEN** 初始启动逻辑和 hydration 后阅读器逻辑都必须保持 preserved-rail 关闭

### Requirement: Runtime Empty Outline Regression Guard
当真实章节页在运行时会渲染成“没有任何可见 outline 内容且没有刻意保留桌面 rail”时，站点校验必须失败。

#### Scenario: Real chapter page would lose outline and preserved rail
- **WHEN** 站点校验为一个非跳转章节页模拟运行时 outline 可见性，并发现没有可见的标题、figures、tables 或 formulas
- **THEN** 除非该页面被显式分类为保留桌面端 outline rail，否则校验必须失败

### Requirement: Figure Caption Fallback
当图片块带有 `Figure N` 风格的 alt 标签，且后面紧跟一个简短的相邻 caption 段落时，即使该段落没有重复完整的 `Figure N ...` 格式，阅读器也必须继续将其注释成 figure card。

#### Scenario: Alt label and short adjacent caption
- **WHEN** 阅读器发现一个图片块，其 alt 文本标识了 figure 编号，且下一个段落是简短、像 caption 的标签
- **THEN** 阅读器必须把该图片块与段落提升为 figure card，以支持 outline 和 figure-link 行为
