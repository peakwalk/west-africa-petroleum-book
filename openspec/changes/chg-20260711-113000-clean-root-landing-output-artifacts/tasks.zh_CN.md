## 1. 清理约束

- [x] 1.1 补齐根目录 landing 输出清理的 OpenSpec proposal、design、tasks 及中文配套文件。
- [x] 1.2 删除 tracked 的根目录 landing 输出文件，并增加保证其继续缺失的回归检查。

## 2. 生成器默认行为对齐

- [x] 2.1 把独立 landing 生成脚本的默认输出改为 `public/`。
- [x] 2.2 更新 `package.json` 脚本别名和站点渲染断言，对齐 public 输出约束。

## 3. 验证

- [x] 3.1 运行针对 landing 的定向回归测试。
- [x] 3.2 重建站点、运行 `test:site`，并校验 OpenSpec 变更。
