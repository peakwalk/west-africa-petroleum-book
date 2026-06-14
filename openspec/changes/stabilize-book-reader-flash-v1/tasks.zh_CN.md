## 1. OpenSpec 与测试契约

- [x] 1.1 为收窄后的 `v1` 范围补齐 flash-stability proposal、design 和 capability spec
- [x] 1.2 在实现前更新 `scripts/test-site-render.sh`，让它断言新的静态侧栏和启动稳定性契约
- [x] 1.3 运行 `npm run test:site`，确认新增断言在实现完成前先失败

## 2. 静态侧栏实现

- [x] 2.1 新建 `scripts/build_static_reader_sidebar.mjs`，解析 `public/book/toc.html`，渲染最终 sidebar projection 标记，并注入到生成后的书籍页面
- [x] 2.2 把新的静态侧栏构建步骤接入 `package.json` 和 `scripts/preview.sh`
- [x] 2.3 更新生成页契约，让 projected sidebar 标记和 active-row 状态直接编码在 HTML 输出中

## 3. 运行时收口与稳定化

- [x] 3.1 从 `theme/index.hbs` 删除 inline sidebar projection bootstrap 逻辑
- [x] 3.2 在保持现有 internal scroller bridge 不变的前提下，从 `theme/custom.js` 删除 runtime sidebar reprojection 逻辑
- [x] 3.3 增加启动阶段布局 transition 门控，以及非结构性的 projected-sidebar 滚动位置持久化

## 4. 验证

- [x] 4.1 运行 `npm run test:site`，直到完整渲染断言全部通过
- [x] 4.2 运行 `sh scripts/test-preview-build.sh`，验证 preview build 已包含静态侧栏步骤
- [x] 4.3 手工冒烟测试代表性的左侧导航跳转，确认可见闪动消失且滚动模型相关行为无回归
