## 新增需求

### 需求：发布英文 Hero 箭头资源
静态站点构建必须将 `assets/icons/homepage/hero-arrow.svg` 发布到 `public/assets/icons/homepage/hero-arrow.svg`。

#### 场景：构建英文首页资源
- **当** 构建静态站点时
- **则** `public/assets/icons/homepage/hero-arrow.svg` 存在
- **并且** 生成的英文首页 Hero 按钮 CSS 可以加载该资源且不出现 404

### 需求：资源发布保持版本边界
构建必须仅在英文公开资源目录中发布 Hero 箭头，并必须保持法文公开目录中不存在该独立首页资源。

#### 场景：法文构建输出保持选择性
- **当** 构建静态站点时
- **则** `public/fr/assets/icons/homepage/hero-arrow.svg` 不存在
- **并且** 法文首页输出和导航保持不变
