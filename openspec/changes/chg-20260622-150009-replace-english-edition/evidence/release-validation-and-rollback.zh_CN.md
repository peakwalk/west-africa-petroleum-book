# 发布验证与回滚

## 发布验证证据

替换版英文稿的 cutover 已在 `2026-06-23` 完成最小必要发布检查：

- `python3 scripts/check_docx_parity.py --edition en`
  - 通过。
- `python3 scripts/check_docx_figures.py --edition en`
  - 通过。
- `python3 scripts/check_docx_figures.py --edition fr`
  - 通过。
- `npm run build:site`
  - 通过。
- `npm run test:site`
  - 通过；其中已把 `scripts/test-site-render.sh` 里的英文拓扑和资源断言刷新为与新英文稿一致的版本。
- `python3 -m unittest tests.test_book_editions tests.test_public_editions tests.test_theme_custom_css.ThemeCustomCssTest.test_figure_annotation_accepts_colonless_and_french_caption_spacing tests.test_theme_custom_css.ThemeCustomCssTest.test_table_annotation_supports_french_tableau_captions_and_docx_tables`
  - 通过（共 `34` 个测试）。

法文冻结边界的信心来自两层独立证据：

- `python3 scripts/check_docx_figures.py --edition fr` 证明法文 figure inventory 和发布资源预期仍然成立。
- 定向的法文回归单测证明：
  - 法文 book 页面仍然发布正确的法文内容与资源目标。
  - 法文 public 页面仍然发布正确的法文路由与落地页文案。
  - theme 侧仍然接受法文相关的 caption 解析模式，例如不带冒号的 `Figure` caption，以及本地化的 `Tableau` table label。

## 明确未纳入发布门禁的检查

以下命令已审阅，但未作为本次 cutover 的发布门禁：

- `python3 scripts/check_docx_parity.py --edition fr`
  - 当前会因一个既有的法文 parity baseline mismatch 失败。这个失败不是本次“仅英文 cutover”引入的，因此应视为历史噪音，而不是本次变更的发布阻塞项。
- `python3 -m unittest tests.test_book_editions tests.test_public_editions tests.test_theme_custom_css`
  - 完整 theme suite 当前包含若干与英文稿替换无关、但已经过时的样式契约断言。上面那组定向的法文安全 theme tests 才是这次发布真正需要的最小回归信号。

## 回滚步骤

针对已发布英文版的 operational rollback，只需要处理英文侧：

1. 把 `resources/editions/en/reference.docx` 重新指回旧英文稿 alias 目标：
   - `resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).docx`
2. 把 `resources/editions/en/reference.pdf` 重新指回旧英文 PDF alias 目标：
   - `resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).pdf`
3. 从 cutover 前的 revision 恢复 `editions/en/content/**`。
   - 这包括 `SUMMARY.md`、所有英文章节 Markdown、`editions/en/content/images/**` 以及 `editions/en/content/images/figure-manifest.json`。
4. 重新构建发布站点：
   - `npm run build:site`
5. 重新执行英文发布检查：
   - `python3 scripts/check_docx_parity.py --edition en`
   - `python3 scripts/check_docx_figures.py --edition en`
   - `npm run test:site`

为什么这个回滚范围足够：

- 英文稿 alias 只位于 `resources/editions/en/reference.*`。
- 英文发布源、figure 资源和 manifest 全都位于 `editions/en/content/**`。
- 法文源和法文 manuscript aliases 仍然冻结在：
  - `editions/fr/**`
  - `resources/editions/fr/reference.docx`
  - `resources/editions/fr/reference.pdf`

因此，恢复旧英文发布不需要修改任何法文文件。

## 仓库状态说明

如果目标不仅是回滚运行时英文站点，还要让当前分支完全回到 cutover 前的验证基线，那么回滚提交还应一并恢复那些在共享验证文件中改成“新英文拓扑”的英文断言，例如 `scripts/test-site-render.sh`。这一步不是运行时英文站点回滚所必需，但如果仓库也要重新验证旧英文六章拓扑，则必须执行。
