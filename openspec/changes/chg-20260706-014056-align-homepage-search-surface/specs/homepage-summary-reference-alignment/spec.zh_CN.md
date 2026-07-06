## ADDED Requirements

### Requirement: 首页 summary-modules 行 MUST 对齐批准的 4 卡片收尾参考图
生成后的英文首页 SHALL 把底部 `summary-modules` 区块渲染成 4 张卡片组成的收尾信息行，并具备批准参考图里的卡片层级、列表样式和可见 CTA 链接，而不是此前那种等宽、无 CTA 的信息卡布局。

#### Scenario: 桌面端布局遵循批准的卡片构图
- **WHEN** 英文首页在桌面宽度下渲染
- **THEN** 这行 summary 卡片会渲染 latest updates、current edition、topics covered 和 future development 这 4 张卡片
- **THEN** current-edition 卡片在视觉上比其它卡片更宽
- **THEN** latest-updates 和 topics-covered 列表会使用绿色勾选样式标记，而不是普通圆点
- **THEN** latest updates、topics covered 和 future development 这 3 张卡片底部都会显示可见的 action link

#### Scenario: Summary 跳转仍然保持站内可用
- **WHEN** 用户点击任意 summary 卡片 CTA
- **THEN** `View all updates` 和 `Learn more` 会继续跳转到现有章节库路由
- **THEN** `View all topics` 会继续跳回首页现有的 topics 锚点
- **THEN** 这次视觉刷新不会要求新增后端或占位页面

#### Scenario: 窄屏下 summary 卡片继续可用
- **WHEN** 首页在平板或手机宽度下渲染
- **THEN** summary 卡片会继续通过现有响应式网格回退规则进行重排
- **THEN** current-edition 的封面图片仍然完整可见，不会被裁切
- **THEN** 列表文案和 CTA 标签在更窄宽度下仍保持可读
