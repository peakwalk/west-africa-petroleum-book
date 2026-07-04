## 为什么

`assets/css/landing.css` 已经膨胀成一个超过 2700 行的手写样式文件。这样会让审查、局部修改和职责边界都变得不必要地困难，尤其是在仓库刚刚加入了针对落地页样式文件的行数指导之后。当前文件把 tokens、header 导航、hero 样式、各类 section 卡片、footer 样式和响应式覆盖全部混在一个源码里。

为了在不改变首页行为的前提下符合新的仓库规则，需要把落地页 CSS 重组为多个更小、更有内聚性的源码文件，同时保持生成站点结果和资源引用方式不变。

## 变更内容

- 按稳定职责把 `assets/css/landing.css` 拆分为多个更小的落地页样式模块。
- 保留 `assets/css/landing.css` 作为对外入口样式文件，这样现有 HTML 引用和资源版本注入逻辑都不需要变化。
- 更新站点渲染验证，使其能够检查模块化后的 CSS 结构，同时不削弱现有的视觉和结构断言。

## 能力

### 新增能力
- `landing-stylesheet-organization`：落地页样式以小而内聚的手写模块维护，同时保留公开的入口样式文件和当前渲染行为。

## 影响

- 受影响源码：`assets/css/landing.css`，以及 `assets/css/` 下新增的 landing CSS 同级拆分文件
- 受影响验证：`scripts/test-site-render.sh`
- 通过 `npm run build:site` 间接影响生成输出
- 不打算改变首页信息架构、文案、路由或视觉行为
