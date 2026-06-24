## 1. OpenSpec 与测试契约

- [x] 1.1 补齐 cross-reference-linker 的 proposal 与 capability spec
- [x] 1.2 为新的 reader 交叉引用链接器契约补上先失败的源码级断言

## 2. Reader 实现

- [x] 2.1 在 `theme/custom.js` 中实现运行时正文交叉引用链接器
- [x] 2.2 复用现有 figure/table 锚点、当前页 section heading 和侧栏 chapter 路由作为目标
- [x] 2.3 对无目标引用保持纯文本，并避免在已有链接或 caption 卡片内部重复加链
- [x] 2.4 扩展链接器，使其支持基于编号公式锚点的 `Equation X.Y` 与 `Formula X.Y` 引用

## 3. 验证

- [x] 3.1 运行定向 Python theme 测试
- [x] 3.2 运行 `npm run build:site`
- [x] 3.3 运行 `sh scripts/test-site-render.sh`
- [x] 3.4 重新运行覆盖 equation-link 支持的定向 theme 测试与 site-render 断言
