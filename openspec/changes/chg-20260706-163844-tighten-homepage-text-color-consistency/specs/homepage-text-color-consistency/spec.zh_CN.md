## ADDED Requirements

### Requirement: 首页白底区块 MUST 使用共享的文本颜色层级
生成后的首页 SHALL 在白底区块中使用一致的文本颜色层级，让标题、描述文案、元信息和交互文字不再依赖各模块自己那组接近但不同的蓝色来表达角色。

#### Scenario: 描述性文案比标题和链接更平静
- **WHEN** 用户扫描 stakeholder strip、country grid、map overview、search surface、topic cards 和 summary cards 等首页白底区块
- **THEN** 这些区块中的 section headings 仍然是 hero 之外最强的一层文字
- **THEN** 描述性正文 SHALL 使用比强调实体名或卡片标题更平静的 supporting text 角色
- **THEN** 日期、缩写和辅助标签等元信息 SHALL 使用比描述性正文更弱的一层角色

#### Scenario: 相邻模块中的同类文本角色不再漂移
- **WHEN** 两个相邻首页模块在白底区域使用同一种语义文本角色
- **THEN** 这些角色 SHALL 共享同一个 token 或同一个视觉角色分配，而不是继续各自使用不同但接近的写死蓝色
- **THEN** 页面层级 MUST NOT 依赖任意的模块级颜色差异来成立

### Requirement: 首页白底交互文字 MUST 共享同一视觉家族
首页白底区域中的 section links、card links 和 chip-like interactive labels SHALL 共享同一条默认交互文字角色和同一条 hover/focus-visible 交互角色，除非批准参考图明确要求更强的例外。

#### Scenario: 白底 CTA 共享同一默认链接基线
- **WHEN** 用户查看 `View All Countries`、country analysis links、topic card links、summary-card links 或 search-scope chips
- **THEN** 这些交互标签 SHALL 来自同一个默认交互文字家族
- **THEN** 它们与周围描述性文案之间仍然保持清晰区分

#### Scenario: 白底 hover 状态彼此相关，而不是继续发明新的蓝色
- **WHEN** 用户 hover 或 focus 任一首页白底文本 CTA
- **THEN** hover 或 focus-visible 状态 SHALL 使用共享交互 hover 家族，而不是模块专属的一次性蓝色
- **THEN** 该 CTA 仍然应当被识别为同一套首页交互系统的一部分
