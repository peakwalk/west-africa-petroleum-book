## Why

landing 构建仍然会把 `assets/icons/homepage-cropped/` 下 10 个历史 PNG 变体复制到英文和法文两个 public 资源目录里，但当前 landing 生成脚本只会引用对应的 WebP 文件。这些 PNG 已经不再属于运行时契约，只会让构建产物额外变大。

这次跟进清理会保持很窄。只删除这组未使用的 cropped icon PNG 副本，保留当前正在使用的 WebP 资源，并把目录说明同步到现在的交付格式。

## What Changes

- 从 `assets/icons/homepage-cropped/` 删除未使用的 PNG 文件。
- 更新 cropped icon 目录的 README，使其描述与当前 WebP 交付契约一致。
- 增加回归校验，确保这些 PNG 变体在源目录和生成后的 public 资源目录中都保持缺失。

## Capabilities

### New Capabilities
- `homepage-cropped-icon-png-cleanup`：landing 源目录和生成资源目录都排除退役的 cropped icon PNG 变体，同时继续交付 WebP 图标集。

### Modified Capabilities
- None.

## Impact

- 从 `assets/icons/homepage-cropped/` 删除的源资源：
  - `icon-audience-operators.png`
  - `icon-audience-policy.png`
  - `icon-audience-research.png`
  - `icon-exploration.png`
  - `icon-fiscal.png`
  - `icon-industry-monitoring.png`
  - `icon-intelligence.png`
  - `icon-production.png`
  - `icon-regulation.png`
  - `icon-research.png`
- 受影响的文档：`assets/icons/homepage-cropped/README.md`、`assets/icons/homepage-cropped/README.zh_CN.md`
- 受影响的校验：`tests/test_public_editions.py`、`scripts/test-site-render.sh`
