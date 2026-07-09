## 1. OpenSpec 与事实源更新

- [x] 1.1 为 landing 图标替换变更补齐 proposal、design、spec 以及对应的中文 companion 文件。

## 2. Landing 图标实现

- [x] 2.1 在保持现有资源路径稳定的前提下，用从网上获取的 SVG 资源替换非 hero-stat landing 图标。
- [x] 2.2 更新 homepage topic-reference helper，让它输出 SVG 图标路径而不是 PNG 路径。
- [x] 2.3 统一法语兼容首页中的图标尺寸，避免新的 SVG 资源被拉伸。
- [x] 2.4 用同一图标源刷新 landing sprite 中的控件图标，同时保留 `currentColor` 行为。

## 3. 验证

- [x] 3.1 更新 site-render 断言，覆盖新的 topic SVG 契约以及相关资源存在性检查。
- [x] 3.2 重建站点并运行最小必要的 landing-page 校验命令。
