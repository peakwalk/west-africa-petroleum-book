## 1. OpenSpec 和失败回归面

- [x] 1.1 为 landing favicon 交付变更补齐 proposal、design、spec 以及中文 companion 文件。
- [x] 1.2 增加会失败的 landing shell 回归检查，覆盖分离后的 favicon 路径和资源体积合约。

## 2. Landing favicon 实现

- [x] 2.1 从现有 favicon 源图生成 `32x32` favicon PNG 和独立的 Apple touch icon PNG。
- [x] 2.2 更新共享 landing 头部生成器，让它引用新的分离 favicon 资源。
- [x] 2.3 刷新构建产物断言，让 landing 输出一旦回退到旧的 oversized shared favicon 路径就直接失败。

## 3. 重建与验证

- [x] 3.1 对新的分离 favicon 合约运行聚焦 landing 生成测试，并完成一次 red-green cycle。
- [x] 3.2 重建站点，运行 landing 验证，并校验 OpenSpec change 文档。
