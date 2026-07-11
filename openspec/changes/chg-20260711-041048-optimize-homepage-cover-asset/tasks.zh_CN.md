## 1. OpenSpec 和失败回归面

- [x] 1.1 为 homepage 封面资源优化变更补齐 proposal、design、spec 以及中文 companion 文件。
- [x] 1.2 增加会失败的 homepage 回归检查，覆盖优化后的封面资源路径、加载提示和体积合约。

## 2. Homepage 封面实现

- [x] 2.1 从现有 PNG 源生成适合 homepage 卡片尺寸的仓库内 WebP 封面资源。
- [x] 2.2 更新共享 homepage 生成器，让 current-edition 封面卡片引用 WebP 资源，并带上 lazy loading 与 async decoding。
- [x] 2.3 刷新构建产物断言，让 homepage 输出一旦回退到沉重的 PNG 封面资源就直接失败。

## 3. 重建与验证

- [x] 3.1 对新的封面交付合约运行聚焦 homepage 生成测试，并完成一次 red-green cycle。
- [x] 3.2 重建站点，运行 landing-page 验证命令，并校验 OpenSpec 变更文档。
