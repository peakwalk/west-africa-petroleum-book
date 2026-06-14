## ADDED Requirements

### Requirement: Static sidebar projection before first paint
The `/book/` reader MUST render its final left-rail sidebar projection from generated HTML before runtime reader JavaScript constructs any sidebar rows. Generated book pages MUST include the projected sidebar markup and the active-row state for the current page.

#### Scenario: Chapter page ships with projected sidebar markup
- **WHEN** a generated `/book/chapters/*.html` page is opened
- **THEN** the page already contains `.reader-sidebar-projection` markup with the active row for that page before runtime reader enhancement code runs

#### Scenario: Root index page ships with projected sidebar markup
- **WHEN** the generated `/book/index.html` page is opened
- **THEN** the page already contains `.reader-sidebar-projection` markup instead of depending on runtime projection construction

### Requirement: No runtime sidebar reprojection after paint
The `/book/` reader MUST NOT rebuild sidebar projection structure from `theme/index.hbs` inline boot logic or from `theme/custom.js` after page paint. Reader enhancement code MAY bind non-structural behavior to projected rows, but it MUST NOT reconstruct the sidebar section and row tree at runtime.

#### Scenario: Template does not bootstrap sidebar projection
- **WHEN** the book template source is inspected
- **THEN** it does not include an inline `bootstrapSidebarProjection()` path that reconstructs projected sidebar rows

#### Scenario: Reader enhancement script does not reproject the sidebar
- **WHEN** the reader enhancement source is inspected
- **THEN** it does not include a runtime `installSidebarProjection()` path that rebuilds sidebar projection structure after page load

### Requirement: Boot-time geometry transitions are suppressed
The `/book/` reader MUST suppress layout-affecting transitions during boot until the reader shell is ready. Geometry tied to sidebar width or reader left-offset MUST NOT animate during initial page load.

#### Scenario: Boot state disables reader geometry motion
- **WHEN** a generated book page is in its boot state
- **THEN** reader geometry transitions such as `padding-inline-start`, `width`, and `margin-inline-start` are disabled until boot completes

#### Scenario: Stable first paint during left-rail navigation
- **WHEN** a reader navigates to another chapter from the left rail
- **THEN** the new page loads without a visible whole-page layout flash caused by delayed sidebar projection or boot-time layout animation

### Requirement: Current scroll model remains unchanged in v1
The `v1` flash stabilization change MUST preserve the existing `#mdbook-reader-scroll` model and MUST NOT remove the internal scroll bridge in the same release.

#### Scenario: Scroll bridge remains present
- **WHEN** the reader enhancement source is inspected after the `v1` change
- **THEN** the internal scroller bridge remains present and the change does not migrate the page back to native document scrolling
