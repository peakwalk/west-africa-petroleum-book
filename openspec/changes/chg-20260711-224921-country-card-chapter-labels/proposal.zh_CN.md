## 背景与动机

英文首页目前将所有国家卡片链接统一标为“Country Analysis”，未体现该国家在书籍中的位置。UA-14 要求首页以已发布英文版的章节编号呈现各国家链接，使 Upstream Atlas 的导航更符合参考书定位，同时不改变原有跳转。

## 变更内容

- 将英文版 16 张国家卡片的链接文案替换为相应的 `Chapter 3.X →`。
- 保持现有章节路径、锚点、卡片标记、样式、悬停行为与响应式布局不变。
- 为每个国家卡片的文案和跳转地址增加生成页面回归测试。
- 法文兼容首页不变：它不渲染英文版的 16 张国家卡片，且章节结构不同。

## 能力

### 新增能力

- `homepage-country-card-chapter-labels`：在首页国家卡片上呈现并验证已发布英文版的章节编号链接文案。

### 修改的能力

无。

## 影响范围

- 受影响源文件：`scripts/shared/homepage-content.mjs`。
- 受影响校验：`tests/test_homepage_country_cards.py` 与 `scripts/test-site-render.sh`。
- 不改变 URL、API、依赖、章节内容、图表或法文版。
