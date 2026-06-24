## ADDED Requirements

### Requirement: Reader body figure images open the original asset in a new browser tab
`/book/` reader MUST 允许用户通过在新浏览器标签页中打开原图资源的方式查看已生成的正文 figure 图片。

#### Scenario: Clicking a body figure image opens the original asset in a new tab
- **WHEN** 用户点击一个位于生成后的 `.reader-article .figure-card` 内部的图片
- **THEN** reader 会在一个新的浏览器标签页里打开该图片资源
- **AND** 当前章节标签页保持不变

#### Scenario: Keyboard activation opens the same image in a new tab
- **WHEN** 焦点位于一个符合条件的正文 figure 图片上
- **AND** 用户按下 `Enter` 或 `Space`
- **THEN** 同一个图片资源会在新的浏览器标签页中打开

#### Scenario: Multi-image figures open the clicked panel only
- **WHEN** 某个生成后的 figure 卡片里包含多张图片
- **AND** 用户激活其中一张图片
- **THEN** 新标签页只打开被激活的那一张图片，而不是整组图片

### Requirement: Reader image-open behavior stays scoped to body figures
`/book/` reader MUST 把图片打开增强限制在已生成的正文 figure 卡片上，并且 MUST NOT 把它绑定到非正文图片。

#### Scenario: Non-body images remain unchanged
- **WHEN** 某张图片位于 `.reader-article .figure-card` 之外，包括导航、封面、落地页或装饰性 chrome 图片
- **THEN** reader 不会把该图片视为本增强可打开对象
- **AND** 新标签页图片打开行为不会绑定到该图片上
