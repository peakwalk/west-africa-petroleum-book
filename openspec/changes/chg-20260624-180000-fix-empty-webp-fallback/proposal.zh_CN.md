## Why

英文版 web book 的 Figure 11 当前加载失败，因为发布素材链路在 `figure-011.webp` 为 0 字节时仍然优先选它，而同目录下其实存在有效的 `figure-011.png`。如果不同时修复素材选择和校验层，后续还会继续静默发布同类坏图。

## What Changes

- 让 figure inventory 在同一 figure stem 下忽略 0 字节候选素材，并自动回退到下一个有效格式。
- 扩展 DOCX figure coverage 校验，在 Markdown 引用或 manifest 选中的 figure 资源为空文件时直接失败。
- 修复当前英文版 Figure 11 的发布素材，确保 `/book/` 现有构建不再输出坏图。
- 重建英文版 figure manifest，确保后续重建继续沿用修正后的素材选择结果。

## Capabilities

### New Capabilities
- `figure-asset-fallback`：Figure 素材发布与校验优先选择非空资源；当首选 WebP 为空文件但 PNG 有效时自动回退到 PNG，并在本会发布空资源时触发校验失败。

### Modified Capabilities
- None.

## Impact

- 受影响源码：`scripts/docx_figures/inventory.py`、`scripts/check_docx_figures.py`、`tests/docx_figures/test_inventory.py`、`tests/test_book_editions.py`
- 受影响素材与元数据：`editions/en/content/images/figure-011.webp`、`editions/en/content/images/figure-manifest.json`
- 重建后受影响产物：`public/book/images/figure-011.webp`、`public/book/images/figure-manifest.json`
- 不引入新的运行时依赖
