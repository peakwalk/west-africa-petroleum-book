## 1. OpenSpec 与失败测试

- [x] 1.1 补齐空 WebP 回退的 proposal、design 与 capability spec。
- [x] 1.2 先补失败测试，覆盖 0 字节 WebP 回退，以及构建后的英文版 Figure 11 资源必须非空。

## 2. 素材发布与校验

- [x] 2.1 更新 `scripts/docx_figures/inventory.py`，让发布素材选择跳过 0 字节文件，并在同一 figure stem 下回退到下一个有效格式。
- [x] 2.2 更新 `scripts/check_docx_figures.py`，让 0 字节 Markdown 目标和 0 字节 manifest 目标都直接失败。

## 3. 修复与验证

- [x] 3.1 重生成英文版 `figure-011.webp`，并重建 `editions/en/content/images/figure-manifest.json`。
- [x] 3.2 运行针对性的 inventory / build 测试与最小 figure coverage 校验，确认修复生效。
- [x] 3.3 重建站点并确认发布后的英文版 Figure 11 资源不再为空文件。
