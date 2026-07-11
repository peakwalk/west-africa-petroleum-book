## 1. OpenSpec 与失败型回归校验

- [x] 1.1 为 cropped icon PNG 清理补齐 proposal、design、spec 以及中文配套文件。
- [x] 1.2 先加入失败型回归校验，要求这些 cropped icon PNG 变体在源目录和构建产物中都保持缺失。

## 2. 源目录清理与文档更新

- [x] 2.1 更新 cropped icon 的 README 文件，使其反映当前 WebP 生产资源契约。
- [x] 2.2 从 `assets/icons/homepage-cropped/` 删除未使用的 PNG 图标副本。
- [x] 2.3 刷新 built-site 断言，让 public 资源目录在这些 PNG 文件回归时也直接失败。

## 3. 重建与验证

- [x] 3.1 按 red-green cycle 运行目标 landing 测试，验证 cropped icon PNG 缺失契约。
- [x] 3.2 重建站点，运行 landing 页面校验，并校验 OpenSpec 变更文档。
