## ADDED Requirements

### Requirement: Public 资源构建排除 source-only 图片备份
当没有任何运行时表面引用时，站点构建 SHALL 不把 source-only 图片备份复制进任一 public 资源树。

#### Scenario: Source-only 图片保持不进入复制后的 public 资源树
- **WHEN** `npm run build:site` 完成
- **THEN** `public/assets/images/upstream-atlas-hero-book.png` 不存在
- **AND** `public/assets/images/prototype-hero-graywhite-left.png` 不存在
- **AND** `public/assets/images/prototype-hero-graywhite-right.png` 不存在
- **AND** `public/fr/assets/images/` 下同样也不存在这三个文件

### Requirement: 法文 public 树排除英文首页专属资源
当法文输出树没有运行时引用时，站点构建 SHALL 不把只属于英文首页的资源复制进 `public/fr/assets/`。

#### Scenario: 法文树省略英文首页专属资源
- **WHEN** `npm run build:site` 完成
- **THEN** `public/fr/assets/images/upstream-atlas-hero-book.webp` 不存在
- **AND** `public/fr/assets/images/homepage-west-africa-map-panel.svg` 不存在
- **AND** `public/fr/assets/icons/homepage-cropped/` 下的 cropped WebP 图标集不存在

### Requirement: 英文根 public 树排除无引用 icon 组
当生成后的英文页面已经改为内联或完全不再使用某些 icon 资源时，站点构建 SHALL 不把这些 icon 文件复制进英文根 public 树。

#### Scenario: 英文根输出省略无引用 icon 组
- **WHEN** `npm run build:site` 完成
- **THEN** `public/assets/icons/country-flags.svg` 不存在
- **AND** `public/assets/icons/homepage/` 目录不存在
- **AND** `public/assets/icons/stakeholders/` 目录不存在
- **AND** `public/assets/icons/topics/` 目录不存在
