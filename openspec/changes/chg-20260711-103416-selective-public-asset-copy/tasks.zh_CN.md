## 1. OpenSpec 与回归校验

- [x] 1.1 为选择性 public 资源复制补齐 proposal、design、spec 以及中文配套文件。
- [x] 1.2 先加入失败型 site-render 断言，覆盖不应再复制的 source-only public 图片和法文树里的英文首页资源。

## 2. 构建资源发布变更

- [x] 2.1 在 `scripts/build_site.mjs` 中用 shared / English-only 资源清单替换整树复制。
- [x] 2.2 在保持当前 landing 和 book 运行时引用不变的前提下，阻止 source-only 图片备份进入两个 public 资源树。

## 3. 重建与验证

- [x] 3.1 按 red-green cycle 运行目标回归校验，验证新的缺失契约。
- [x] 3.2 重建站点，运行 `test:site`，并校验 OpenSpec 变更文档。
