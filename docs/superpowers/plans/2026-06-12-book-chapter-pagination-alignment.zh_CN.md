# Book Chapter Pagination Alignment 实施计划

> **面向代理式工作者：** 必须使用 `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans` 子技能，按任务逐步执行本计划。步骤使用复选框（`- [ ]`）语法跟踪。

**目标：** 让书籍阅读器的章节分页对齐已批准的宽屏和窄屏设计，同时不改变 mdBook 的章节数据流或模板结构。

**架构：** 保持 `theme/index.hbs` 不变，在 `theme/custom.css` 中重写分页布局模型，只在宽屏上启用 `theme/custom.js` 的运行时等高逻辑，并在改动生产代码前先更新基于 shell 的回归脚本以编码新的布局契约。

**技术栈：** mdBook 主题模板、CSS、vanilla JavaScript、基于 shell 的回归检查

---

### Task 1: 先在测试中编码新的分页契约

**Files:**
- Modify: `scripts/test-book-pagination-render.sh`
- Reference: `docs/superpowers/specs/2026-06-12-book-chapter-pagination-alignment-design.zh_CN.md`

- [ ] **Step 1: 写出会先失败的回归断言**

新增以下断言：

```sh
width: min(100%, var(--reader-article-body-width));
display: grid;
grid-template-columns: repeat(2, minmax(0, 1fr));
min-height: 92px;
padding: 12px 16px;
width: 44px;
height: 44px;
font-size: 16px;
font-size: 10px;
gap: 12px;
padding: 12px 14px;
justify-items: center;
text-align: center;
```

- [ ] **Step 2: 运行分页脚本，确认它先失败**

运行：`sh scripts/test-book-pagination-render.sh`

预期：由于实现仍然使用旧的 `224px` / `80px` 布局模型，新的宽屏/窄屏分页断言会失败。

### Task 2: 重建宽屏分页布局模型

**Files:**
- Modify: `theme/custom.css:2068-2259`
- Reference: `theme/index.hbs:569-600`

- [ ] **Step 1: 替换宽屏容器布局**

把容器从 flex 分布改为等宽 grid：

```css
.chapter-pagination {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  align-items: stretch;
  gap: 12px;
  width: min(100%, var(--reader-article-body-width));
  max-width: none;
  margin-top: 24px;
  margin-inline: auto;
}
```

- [ ] **Step 2: 替换宽屏卡片尺寸 token**

让卡片填满 grid，而不是限制在 `224px`：

```css
.chapter-nav-card {
  width: 100%;
  max-width: none;
  min-height: 92px;
  height: auto;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 12px;
}
```

- [ ] **Step 3: 更新宽屏徽标、文字和装饰尺寸**

设置宽屏排版与装饰 token：

```css
.chapter-nav-badge { width: 44px; height: 44px; }
.chapter-nav-arrow { font-size: 24px; }
.chapter-nav-card[data-chapter-badge-type="number"] .chapter-nav-arrow { font-size: 20px; }
.chapter-nav-label { font-size: 11px; line-height: 13px; letter-spacing: 0.08em; }
.chapter-nav-title { font-size: 16px; line-height: 1.08; }
.chapter-nav-dek { font-size: 10px; line-height: 1.3; max-width: none; }
.chapter-nav-card::after { width: 68px; height: 60px; opacity: 0.12; }
```

- [ ] **Step 4: 运行分页脚本，确认宽屏规则通过而窄屏规则仍失败**

运行：`sh scripts/test-book-pagination-render.sh`

预期：只会在窄屏断言或仍反映旧行为的 JS 断言上失败。

### Task 3: 重建窄屏分页布局模型

**Files:**
- Modify: `theme/custom.css:3998-4086`

- [ ] **Step 1: 更新堆叠容器间距**

替换旧的窄屏 gap 和顶部间距行为：

```css
.chapter-pagination {
  gap: 12px;
  margin-top: 16px;
}
```

- [ ] **Step 2: 替换窄屏卡片 token**

使用新的堆叠卡片尺寸：

```css
.chapter-nav-card {
  width: 100%;
  height: auto;
  min-height: 92px;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 12px;
}
```

- [ ] **Step 3: 重建窄屏上一章和下一章 grid 模板**

应用非对称三列布局：

```css
.chapter-nav-previous {
  grid-template-columns: 44px minmax(0, 1fr) 72px;
}

.chapter-nav-next {
  grid-template-columns: 72px minmax(0, 1fr) 44px;
}
```

- [ ] **Step 4: 更新窄屏文字对齐、徽标尺寸和装饰尺寸**

应用窄屏排版与下一张卡片居中规则：

```css
.chapter-nav-badge { width: 44px; height: 44px; }
.chapter-nav-arrow { font-size: 24px; }
.chapter-nav-card[data-chapter-badge-type="number"] .chapter-nav-arrow { font-size: 20px; }
.chapter-nav-label { font-size: 12px; line-height: 14px; }
.chapter-nav-title { font-size: 16px; line-height: 17px; }
.chapter-nav-dek { font-size: 10px; line-height: 13px; }
.chapter-nav-next .chapter-nav-body { justify-items: center; text-align: center; }
.chapter-nav-next .chapter-nav-label { justify-self: center; }
.chapter-nav-card::after { width: 72px; height: 60px; bottom: 8px; opacity: 0.13; }
```

- [ ] **Step 5: 运行分页脚本，确认只剩 JS 相关断言**

运行：`sh scripts/test-book-pagination-render.sh`

预期：CSS 布局检查通过；若仍有失败，应指向仍然全局启用的运行时等高行为。

### Task 4: 将运行时等高行为限制到宽屏

**Files:**
- Modify: `theme/custom.js:2046-2088`

- [ ] **Step 1: 为等高同步添加宽屏门控**

使用 `window.matchMedia("(min-width: 761px)")` 进行保护，并在窄屏时清除内联高度：

```js
const widePaginationMediaQuery = window.matchMedia("(min-width: 761px)");

if (!widePaginationMediaQuery.matches) {
  cards.forEach(function (card) {
    card.style.height = "";
  });
  return;
}
```

- [ ] **Step 2: 重新运行分页脚本，确认它通过**

运行：`sh scripts/test-book-pagination-render.sh`

预期：PASS

### Task 5: 运行完整验证

**Files:**
- Verify: `theme/custom.css`
- Verify: `theme/custom.js`
- Verify: `scripts/test-book-pagination-render.sh`

- [ ] **Step 1: 运行完整站点渲染检查**

运行：`npm run test:site`

预期：PASS，并输出 `Site render checks passed.`

- [ ] **Step 2: 检查最终 diff，控制变更范围**

运行：`git diff -- theme/custom.css theme/custom.js scripts/test-book-pagination-render.sh docs/superpowers/plans/2026-06-12-book-chapter-pagination-alignment.md`

预期：只包含分页样式、分页 JS 行为、回归检查，以及新的计划文档。
