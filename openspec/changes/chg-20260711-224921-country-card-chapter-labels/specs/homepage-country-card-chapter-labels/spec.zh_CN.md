## 新增需求

### 需求：英文国家卡片展示已发布的章节标签
生成的英文首页必须渲染恰好 16 个国家卡片分析链接。每个链接必须为对应国家展示已发布英文版的 `Chapter 3.X →` 标签：

| 国家 | 标签 |
| --- | --- |
| Nigeria | `Chapter 3.1 →` |
| Ghana | `Chapter 3.2 →` |
| Côte d'Ivoire | `Chapter 3.3 →` |
| Senegal | `Chapter 3.4 →` |
| Mauritania | `Chapter 3.5 →` |
| Niger | `Chapter 3.6 →` |
| Benin | `Chapter 3.7 →` |
| Liberia | `Chapter 3.8 →` |
| Sierra Leone | `Chapter 3.9 →` |
| Guinea | `Chapter 3.10 →` |
| Guinea-Bissau | `Chapter 3.11 →` |
| The Gambia | `Chapter 3.12 →` |
| Togo | `Chapter 3.13 →` |
| Burkina Faso | `Chapter 3.14 →` |
| Mali | `Chapter 3.15 →` |
| Cabo Verde | `Chapter 3.16 →` |

#### 场景：英文首页渲染全部章节标签
- **当** 生成英文首页时
- **则** 16 张国家卡片均具有其国家对应的规定标签
- **并且** 没有国家卡片分析链接显示 `Country Analysis →`

### 需求：国家卡片的目标地址保持不变
每个生成的英文国家卡片分析链接必须保留原有章节 URL 与国家片段锚点。

#### 场景：国家卡片标签保留其目标地址
- **当** 使用章节标签生成英文首页时
- **则** 每个国家卡片分析链接具有与本变更前相同的 `href`
- **并且** 每个 `href` 均指向英文第 3 章国家分析页面及其国家专属片段锚点

### 需求：其他版本与展示保持稳定
本变更不得修改法文兼容首页的国家导航行为，也不得更改英文卡片链接已有的标记类或展示规则。

#### 场景：生成版本页面保持既有展示契约
- **当** 本变更后生成英文和法文首页时
- **则** 英文卡片分析链接保留 `country-analysis-link` 类和现有目标地址格式
- **并且** 法文兼容首页保留现有的国家导航输出
