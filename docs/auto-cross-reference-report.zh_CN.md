# 自动交叉引用报告

快照日期：2026-06-24

这份报告记录了截至当前快照，web book 中“正文自动链接器”在运行时真实生效的位置。

## 范围

- 事实来源：`/book/` 与 `/fr/book/` 渲染后的页面，并且以 reader 运行时 JavaScript 执行完成后的 DOM 为准。
- 统计规则：只统计最终渲染出来的 `a.reader-cross-reference-link`。
- 设计上排除的区域：
  - `List of Figures`、`List of Tables`、`List of Equations`
  - figure/table/formula 卡片外壳
  - 已有链接
  - heading 标题

因此，这份报告反映的是最终 reader 行为，而不是原始 Markdown 的文本匹配结果。

## 复核方法

1. 运行 `npm run build:site` 构建站点。
2. 本地服务化 `public/` 目录。
3. 用 headless Chrome 打开已发布章节页。
4. 从最终 DOM 中枚举 `a.reader-cross-reference-link` 节点。

## 英文版

当前实际生效的自动链接共 35 处。

### 页面：General Introduction

来源：[chapter-01-general-introduction.md](/Users/edison/workspace/peakwalk/scm/gitlab/africa-book/editions/en/content/chapters/chapter-01-general-introduction.md:73)

- 第 73 行：`Chapter 2`
- 第 75 行：`Chapter 3`
- 第 77 行：`Chapter 4`
- 第 79 行：`Chapter 5`
- 第 81 行：`Chapter 6`
- 第 83 行：`Chapter 7`
- 第 85 行：`Chapter 8`
- 第 87 行：`Chapter 9`
- 第 89 行：`Chapter 10`
- 第 91 行：`Chapter 11`
- 第 93 行：`Chapter 12`

### 页面：Hydrocarbon Value Chain

来源：[chapter-05-hydrocarbon-value-chain.md](/Users/edison/workspace/peakwalk/scm/gitlab/africa-book/editions/en/content/chapters/chapter-05-hydrocarbon-value-chain.md:55)

- 第 55 行：`Table 2`
- 第 120 行：`Table 3`
- 第 190 行：`Figure 8`
- 第 214 行：`Table 4`
- 第 448 行：`Table 5`
- 第 745 行：`Figure 9`

### 页面：Upstream Operations and Government Roles

来源：[chapter-06-upstream-operations-and-government-roles.md](/Users/edison/workspace/peakwalk/scm/gitlab/africa-book/editions/en/content/chapters/chapter-06-upstream-operations-and-government-roles.md:15)

- 第 15 行：`Figure 15`
- 第 998 行：`Figure 17`
- 第 1010 行：`Figure 18`
- 第 1030 行：`Figure 19`
- 第 1030 行：`Figure 20`
- 第 1112 行：`Figure 22`
- 第 1134 行：`Figure 23`
- 第 1667 行：`Figure 28`
- 第 1669 行：`Figure 29`

### 页面：West African Fiscal Regimes

来源：[chapter-08-west-african-fiscal-regimes.md](/Users/edison/workspace/peakwalk/scm/gitlab/africa-book/editions/en/content/chapters/chapter-08-west-african-fiscal-regimes.md:590)

- 第 590 行：`Section 8.5`
- 第 866 行：`Figure 72`
- 第 866 行：`Figure 73`
- 第 866 行：`Figure 74`
- 第 866 行：`Figure 75`
- 第 866 行：`Figure 76`
- 第 866 行：`Figure 77`
- 第 1859 行：`Table 17`
- 第 1859 行：`Figure 79`

## 法文版

当前实际生效的自动链接共 14 处。

### 页面：Value Chain of the Hydrocarbon Sector

来源：[chapter-01-value-chain-of-the-hydrocarbon-sector.md](/Users/edison/workspace/peakwalk/scm/gitlab/africa-book/editions/fr/content/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md:29)

- 第 29 行：`Tableau 1`
- 第 104 行：`Tableau 2`
- 第 294 行：`Figure 4`

### 页面：Different Phases of Upstream Oil and the Roles of States

来源：[chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md](/Users/edison/workspace/peakwalk/scm/gitlab/africa-book/editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md:41)

- 第 41 行：`Figure 6`
- 第 101 行：`Figure 7`
- 第 109 行：`Figure 9`
- 第 119 行：`Figure 10`
- 第 149 行：`Figure 13`
- 第 155 行：`Figure 15`
- 第 608 行：`Figure 20`

### 页面：Tax Regimes in the Petroleum Sector

来源：[chapter-03-tax-regimes-in-the-petroleum-sector.md](/Users/edison/workspace/peakwalk/scm/gitlab/africa-book/editions/fr/content/chapters/chapter-03-tax-regimes-in-the-petroleum-sector.md:3)

- 第 3 行：`Figure 21`
- 第 13 行：`Figure 22`
- 第 39 行：`Figure 23`

### 页面：Comparative Study of Tax Regimes in Selected West African Countries

来源：[chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md](/Users/edison/workspace/peakwalk/scm/gitlab/africa-book/editions/fr/content/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md:132)

- 第 132 行：`Figure 24`

## 当前边界

### Equation / Formula 链接

运行时链接器现在已经支持 `Equation X.Y` 与 `Formula X.Y`。

但截至当前快照，英文版与法文版正文页面里都还没有出现符合该契约的编号公式引用文本，因此 reader 中当前真实生效的 equation 链接命中数仍为 0。

### 索引页

以下页面按设计不会生成 `reader-cross-reference-link`，因为链接器会跳过 `.reference-index`：

- `list-of-figures.html`
- `list-of-tables.html`
- `list-of-equations.html`

## 为什么运行时统计会比原始文本扫描更少

原始 Markdown 扫描会高估，因为它会把这些内容也算进去：

- caption 文本
- 索引页
- figure/table/formula 卡片外壳
- 生成结构中的重复引用

运行时报告才是正确的回归基线，因为它对应的是读者最终能够点击到的内容。
