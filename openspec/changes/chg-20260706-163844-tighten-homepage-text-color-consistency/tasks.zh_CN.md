## 1. OpenSpec 范围与样式基线

- [x] 1.1 为首页文本颜色一致性变更补齐 proposal、design、spec 以及中文配套文件。
- [x] 1.2 在修改模块样式之前，先识别当前首页白底区块的文本角色，并把它们映射到更小的一组共享 token。

## 2. 首页文本角色收敛

- [x] 2.1 在 `assets/css/landing.base.css` 中新增或规范首页共享文本颜色 token，覆盖标题、辅助正文、元信息和交互文字。
- [x] 2.2 更新白底首页模块，让它们使用这些共享角色，包括 navigation、stakeholder cards、country cards、search chips、topic cards 和 summary cards，同时保持现有布局与文案不变。
- [x] 2.3 检查首页响应式覆盖层，清理会在 tablet 或 mobile 上破坏同一层级关系的残留写死蓝色。
- [x] 2.4 只在批准截图对比证明当前结果过轻的地方，把承载内容的短副信息和空状态文案从 metadata 角色重新提升到 supporting body 角色。
- [x] 2.5 在不改布局和文案的前提下，通过排版和 border/shadow 处理强化白底 links、stakeholder cards 和 search chips 的共享 CTA / 控件感。
- [x] 2.6 对 country cards、topic cards 和 summary cards 做最后一轮局部密度微调，在不重开整页层级的前提下，把剩余白底模块拉近到批准截图。
- [x] 2.7 在保留现有 hero metric 结构和 CSS 挂载点不变的前提下，直接用用户提供的 V10 素材原地替换 6 个 hero-stat SVG 资源文件。
- [x] 2.8 在保留现有 topic card 布局和 class hooks 不变的前提下，用用户当前批准的 SVG 素材替换 6 个 topic-card 内联图标。

## 3. 验证

- [x] 3.1 运行与首页样式最相关的最小必要验证，确认没有引入布局、跳转目标或文案回归。
- [x] 3.2 结合批准的页面构图目标复查最终文本层级，确认说明性文案明显比交互文字更平静，且链接共享同一家族的视觉表达。
- [x] 3.3 再次对照批准截图，确认白底区块不再因为 body text 或 CTA 被压得过轻而显得比参考稿更空、更稀。
