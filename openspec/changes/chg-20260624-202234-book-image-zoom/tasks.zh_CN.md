## 1. OpenSpec 与源码级检查

- [x] 1.1 更新 proposal、design 和 `book-reader-image-zoom` capability spec，使其描述“正文 figure 图片在浏览器新标签页中打开原图”的方案。
- [x] 1.2 替换 theme 与 site-render 断言，使其覆盖新标签页契约以及 vendored 依赖已被移除这一事实。

## 2. 依赖回滚

- [x] 2.1 从两个 edition 的 `book.toml` 里移除 vendored pan/zoom helper 的主题加载。
- [x] 2.2 删除已 check-in 的 pan/zoom vendor 文件和来源说明。

## 3. Reader 图片打开实现

- [x] 3.1 用轻量的新标签页图片打开器替换 `theme/custom.js` 中的自定义正文 figure viewer。
- [x] 3.2 保持符合条件的 figure 图片可被键盘聚焦，并支持点击与 `Enter`/`Space` 激活。
- [x] 3.3 保持行为范围仅限 `.reader-article .figure-card img`，并且在多图 figure 中只打开被激活的那张图片。
- [x] 3.4 从 `theme/custom.css` 中移除过期的 overlay-viewer 样式，同时保留键盘 focus affordance。

## 4. 验证

- [x] 4.1 运行覆盖 `theme/custom.js` 与 `theme/custom.css` 的针对性 Python theme 测试。
- [x] 4.2 运行 `sh scripts/test-site-render.sh`。
- [x] 4.3 运行最小必要的 site build/test 命令，确认 reader 输出仍然正常渲染。
