## Why

当前 reader 已经会给带编号的 equation 做注解，并在右侧 outline rail 中暴露出来，但 front matter 里只有 figures 和 tables 的静态索引页。想从全书范围浏览公式的读者，目前无法通过 front matter 或章节库进入一个专门的公式索引页。

因此需要补一个一等公民的 `List of Equations` 页面：它应当和 `List of Tables` 并列，复用同一套 reference-index 展示方式，并且只链接那些已经被明确编号、可以稳定导航的 equation。

## What Changes

- 在英文和法文 edition 中新增一个 front-matter `List of Equations` 页面，位置紧跟在 `List of Tables` 之后。
- 复用现有的 numbered-equation anchor 约定，让新页面直接链接到稳定的 `#formula-*` 目标，而不是再引入第二套公式索引机制。
- 扩展 reader 的 front-matter page-variant 逻辑和发布断言，使新的 equation index 与现有 figure/table index 的行为保持一致。

## Impact

- 预计会影响 `editions/*/content/SUMMARY.md`、各 edition 的 `list-of-equations.md` 页面、`theme/index.hbs`、`theme/custom.js` 以及站点测试。
- 本变更不修改公式提取规则，也不重排现有公式编号；它只把已经编号的公式通过 front matter 索引页暴露出来。
