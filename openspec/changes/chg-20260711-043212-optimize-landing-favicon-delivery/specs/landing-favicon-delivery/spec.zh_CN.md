## ADDED Requirements

### Requirement: Landing shell uses split favicon delivery
landing 页面 SHALL 使用一张更小的专用 PNG 交付浏览器 favicon，并使用另一张更大的 PNG 交付 Apple touch icon，而不是继续把同一张 oversized shared favicon 资源复用于所有图标关系。

#### Scenario: Landing homepage uses the small favicon and separate touch icon
- **WHEN** 英文 landing 首页渲染 `<head>`
- **THEN** `rel="icon"` 引用 `assets/images/upstream-atlas-favicon-32.png`
- **AND** `rel="shortcut icon"` 引用 `assets/images/upstream-atlas-favicon-32.png`
- **AND** `rel="apple-touch-icon"` 引用 `assets/images/upstream-atlas-apple-touch-icon.png`
- **AND** landing 首页头部不再引用 `assets/images/upstream-atlas-favicon.png`

#### Scenario: French landing shell keeps the same split favicon contract
- **WHEN** 法文 landing 首页渲染 `<head>`
- **THEN** `rel="icon"` 引用 `assets/images/upstream-atlas-favicon-32.png`
- **AND** `rel="shortcut icon"` 引用 `assets/images/upstream-atlas-favicon-32.png`
- **AND** `rel="apple-touch-icon"` 引用 `assets/images/upstream-atlas-apple-touch-icon.png`
