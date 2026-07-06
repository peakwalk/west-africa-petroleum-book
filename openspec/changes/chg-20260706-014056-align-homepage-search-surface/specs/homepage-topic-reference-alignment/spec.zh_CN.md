## ADDED Requirements

### Requirement: 首页 Browse by Topic 区块 MUST 对齐批准的 6 卡片 topic 参考图
生成后的英文首页 SHALL 把 `Browse by Topic` 区块渲染成一个紧凑的 6 张 topic 导航卡片区域，并只保留一个可见区块标题，而不是此前那种大 editorial 标题加 10 张信息卡的结构。

#### Scenario: 桌面端布局遵循批准的 topic 构图
- **WHEN** 英文首页在桌面宽度下渲染
- **THEN** 这个区块只显示一个可见标题，文本为 `Browse by Topic`
- **THEN** 这个区块只渲染 6 张主题卡片，分别对应 petroleum value chain、West African fiscal regimes、national oil companies、upstream operations、governance & regulation，以及 country analysis
- **THEN** 每张卡片都显示前置图标、topic 标题、简洁的说明文案，以及一个 `Explore` 链接
- **THEN** 旧的大段 narrative heading 不再作为可见内容出现在这个区块中

#### Scenario: Topic 跳转目标保持不变
- **WHEN** 用户点击英文首页任意一张 `Browse by Topic` 卡片
- **THEN** 每张卡片都继续跳转到首页生成器当前使用的对应章节目标
- **THEN** petroleum value chain、West African fiscal regimes、national oil companies、upstream operations、governance & regulation，以及 country analysis 的目标地址不会因为这次视觉改版而改变

#### Scenario: 窄屏和法文 fallback 继续可用
- **WHEN** 首页在平板或手机宽度下渲染
- **THEN** 英文 topic 卡片会在共享 landing 内容宽度内回流排布，不会裁掉图标或链接文案
- **THEN** 更窄宽度下卡片文案仍然保持可读
- **THEN** 法文兼容首页继续保留它自己的 compact topic fallback 布局，而不会套用英文 reference-grid class
