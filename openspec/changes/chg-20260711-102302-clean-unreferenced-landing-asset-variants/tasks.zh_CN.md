## 1. OpenSpec 与失败型回归校验

- [x] 1.1 为这次无引用 landing 资源清理补齐 proposal、design、spec 以及中文配套文件。
- [x] 1.2 先加入失败型回归断言，要求这些无引用历史资源在源目录和构建产物目录中都保持缺失。

## 2. 源资源清理

- [x] 2.1 在不触碰 graywhite book-theme 活跃资源链的前提下，从 `assets/images/` 删除这批无引用历史资源变体。
- [x] 2.2 刷新 site-render 断言，让源目录和 public 资源目录在这些变体回归时直接失败。

## 3. 重建与验证

- [x] 3.1 按 red-green cycle 运行目标 landing 测试，验证这批无引用资源的缺失契约。
- [x] 3.2 重建站点，运行 landing 页面校验，并校验 OpenSpec 变更文档。
