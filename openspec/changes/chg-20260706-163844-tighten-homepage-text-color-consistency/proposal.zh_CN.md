## Why

当前首页白底区块在标题、正文、元信息和交互文字上混用了多组非常接近的蓝色。即使布局已经基本对齐批准参考图，这种颜色漂移仍然会让 landing page 看起来像是几套相邻模块各自来自不同系统。

用户这次已经明确要求围绕“文本颜色一致性”做评审并继续修正。因此我们需要一个范围很窄的首页变更，只收敛这些文字颜色角色，不重新打开最近几轮已经批准的布局、文案、跳转目标和整体视觉方向。

## What Changes

- 为首页白底区块引入更紧的文本颜色角色集，让标题、辅助说明、元信息和交互文字不再互相争抢注意力。
- 在首页 CSS 中，把语义相同但当前写死的近似蓝色替换成共享 token 或共享角色分配。
- 降低 summary cards、topic cards、search chips 以及说明性文案里对强调蓝的滥用，让可点击文字继续保持明显的交互身份。
- 保持当前首页布局、卡片构成、图标、文案和跳转目标不变，只调整文本颜色层级，以及最少量相关 hover 状态的颜色分配。

## Capabilities

### New Capabilities
- `homepage-text-color-consistency`：首页白底内容区 SHALL 使用一致的文本颜色层级，标题、描述文案、元信息和交互文字遵循统一视觉角色，而不是继续由各模块各自使用接近但不同的蓝色。

### Modified Capabilities
- None.

## Impact

- 受影响的 landing token 与共享颜色：`assets/css/landing.base.css`
- 受影响的首页区块样式：`assets/css/landing.header.css`、`assets/css/landing.discovery.css`、`assets/css/landing.homepage-v2.css`、`assets/css/landing.modules.css`、`assets/css/landing.components.css`
- 如果某些文本角色需要在平板或手机上跟进，可能会影响响应式细节：`assets/css/landing.responsive-tablet.css`、`assets/css/landing.responsive-mobile.css`
- 受影响的验证：覆盖首页样式的聚焦 site-render 或 CSS 断言
- 不预期修改路由、文案、素材或结构性 HTML
