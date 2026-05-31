# Book Reading UI Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the `/book/` reader shell so it preserves the real mdBook sidebar on the left, shows readable content immediately on the right, and visually aligns that reader shell to the approved `figma-prototype`.

**Architecture:** Keep mdBook as the only content and navigation engine. Treat `nav#mdbook-sidebar` as the sole left navigation surface and rebuild only the right-hand shell in `theme/index.hbs`, `theme/custom.css`, and `theme/custom.js` so `#mdbook-content` becomes a two-column `main + outline` reader instead of a fake three-column grid. Use `scripts/test-site-render.sh` as the TDD harness by asserting the correct shell structure, source tokens, and generated output markers before implementation.

**Tech Stack:** mdBook, Handlebars theme template, CSS, vanilla JavaScript, shell-based render assertions

---

**File Map**

- `theme/index.hbs`: owns the reader shell structure; must preserve the mdBook sidebar outside the content shell and define only the right-hand `main + outline` layout.
- `theme/custom.css`: owns all reader-shell geometry, sidebar styling, toolbar styling, responsive rules, and typography rhythm.
- `theme/custom.js`: owns only DOM glue for progress updates and moving the generated `On This Page` block into the right rail.
- `scripts/test-site-render.sh`: owns red-green verification of the source theme files and generated HTML.

### Task 1: Add Failing Assertions For The Correct Reader Model

**Files:**
- Modify: `scripts/test-site-render.sh`
- Test: `scripts/test-site-render.sh`

- [ ] **Step 1: Add failing assertions that encode the correct layout model**

Insert the following checks in `scripts/test-site-render.sh` near the existing `public/book/index.html` and `theme/custom.css` assertions:

```sh
check_contains public/book/index.html 'id="mdbook-sidebar"'
check_contains public/book/index.html 'class="reader-layout"'
check_contains public/book/index.html 'class="reader-main"'
check_contains public/book/index.html 'class="reader-outline"'
check_contains public/book/index.html 'class="reader-article"'
check_contains public/book/index.html 'class="book-sidebar-shell"'
check_contains public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'class="reader-layout"'
check_contains public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'class="reader-main"'
check_contains public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'class="reader-outline"'
check_contains public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'class="reader-article"'
check_contains theme/custom.css '.reader-layout {'
check_contains theme/custom.css 'grid-template-columns: minmax(0, 1fr) minmax(14rem, 17rem);'
check_contains theme/custom.css '.book-sidebar-shell {'
check_contains theme/custom.css 'width: clamp(18rem, 22vw, 21rem);'
check_contains theme/custom.css '.reader-outline {'
check_contains theme/custom.js 'document.body.classList.add("book-outline-ready")'
check_not_contains public/book/index.html 'class="book-shell-grid"'
check_not_contains public/book/index.html 'class="book-page-surface"'
check_not_contains public/book/index.html 'class="book-main-column"'
```

- [ ] **Step 2: Run the render test to verify it fails for the new reader markers**

Run:

```bash
npm run test:site
```

Expected: FAIL with a missing pattern such as `class="reader-layout"` or a missing CSS selector such as `.reader-layout {`, proving the test is checking the new model instead of the previous incorrect one.

- [ ] **Step 3: Commit the red test**

```bash
git add scripts/test-site-render.sh
git commit -m "test: assert corrected book reader layout"
```

### Task 2: Rebuild The Template Around The Real mdBook Sidebar

**Files:**
- Modify: `theme/index.hbs`
- Test: `scripts/test-site-render.sh`

- [ ] **Step 1: Replace the right-hand shell structure without introducing a fake left column**

Update the reader shell section in `theme/index.hbs` so the mdBook sidebar remains external and `#mdbook-content` contains only `main + outline`. The updated content shell should follow this shape:

```hbs
<div id="mdbook-content" class="content reader-layout">
    <main class="reader-main">
        <article class="reader-article">
            {{{ content }}}
        </article>

        <nav class="chapter-pagination" aria-label="Chapter navigation">
            {{#if previous}}
            <a rel="prev" href="{{ path_to_root }}{{ previous.link }}" class="chapter-nav-card chapter-nav-previous">
                <span class="chapter-nav-label">Previous chapter</span>
                <strong>{{ previous.name }}{{ previous.title }}</strong>
            </a>
            {{else}}
            <span class="chapter-nav-card chapter-nav-placeholder" aria-hidden="true"></span>
            {{/if}}

            {{#if next}}
            <a rel="next prefetch" href="{{ path_to_root }}{{ next.link }}" class="chapter-nav-card chapter-nav-next">
                <span class="chapter-nav-label">Next chapter</span>
                <strong>{{ next.name }}{{ next.title }}</strong>
            </a>
            {{/if}}
        </nav>
    </main>

    <aside class="reader-outline">
        <div class="book-outline-inner">
            <p class="book-outline-label">On This Page</p>
            <div class="book-outline-body"></div>
        </div>
    </aside>
</div>
```

Also add the sidebar shell class on the existing mdBook sidebar element:

```hbs
<nav id="mdbook-sidebar" class="sidebar book-sidebar-shell" aria-label="Table of contents">
```

Leave these items intact:

- `{{{ content }}}`
- `id="mdbook-sidebar"`
- search wrapper ids and controls
- theme switcher ids and controls
- progress bar element
- previous/next data source

- [ ] **Step 2: Simplify the toolbar markup to match the prototype density**

Keep the same controls but reduce the shell to a lighter structure:

```hbs
<header id="mdbook-menu-bar" class="menu-bar sticky bordered">
    <div class="book-toolbar">
        <div class="toolbar-left">
            <label id="mdbook-sidebar-toggle" class="icon-button" for="mdbook-sidebar-toggle-anchor" title="Toggle Table of Contents" aria-label="Toggle Table of Contents" aria-controls="mdbook-sidebar">
                {{fa "solid" "bars"}}
            </label>
            <a class="book-home-link" href="{{ path_to_root }}../" aria-label="Back to landing page">
                <img class="book-home-icon" src="{{ path_to_root }}../assets/images/upstream-atlas-icon.png" alt="">
                <span class="book-home-label">Upstream Atlas</span>
            </a>
        </div>

        <div class="toolbar-right">
            {{#if search_enabled}}
            <button id="mdbook-search-toggle" class="icon-button" type="button" title="Search (`/`)" aria-label="Toggle Searchbar" aria-expanded="false" aria-keyshortcuts="/ s" aria-controls="mdbook-searchbar">
                {{fa "solid" "magnifying-glass"}}
            </button>
            {{/if}}
            <button id="mdbook-theme-toggle" class="icon-button" type="button" title="Change theme" aria-label="Change theme" aria-haspopup="true" aria-expanded="false" aria-controls="mdbook-theme-list">
                {{fa "solid" "paintbrush"}}
            </button>
            <ul id="mdbook-theme-list" class="theme-popup" aria-label="Themes" role="menu">
                <li role="none"><button role="menuitem" class="theme" id="mdbook-theme-default_theme">Auto</button></li>
                <li role="none"><button role="menuitem" class="theme" id="mdbook-theme-light">Light</button></li>
                <li role="none"><button role="menuitem" class="theme" id="mdbook-theme-rust">Rust</button></li>
                <li role="none"><button role="menuitem" class="theme" id="mdbook-theme-coal">Coal</button></li>
                <li role="none"><button role="menuitem" class="theme" id="mdbook-theme-navy">Navy</button></li>
                <li role="none"><button role="menuitem" class="theme" id="mdbook-theme-ayu">Ayu</button></li>
            </ul>
            {{#if print_enable}}
            <a class="icon-button toolbar-link" href="{{ path_to_root }}print.html" title="Print this book" aria-label="Print this book">
                {{fa "solid" "print" "print-button"}}
            </a>
            {{/if}}
            {{#if git_repository_url}}
            <a class="icon-button toolbar-link" href="{{ git_repository_url }}" title="Git repository" aria-label="Git repository">
                {{fa git_repository_icon_class git_repository_icon}}
            </a>
            {{/if}}
            {{#if git_repository_edit_url}}
            <a class="icon-button toolbar-link" href="{{ git_repository_edit_url }}" title="Suggest an edit" aria-label="Suggest an edit" rel="edit">
                {{fa "solid" "pencil" "git-edit-button"}}
            </a>
            {{/if}}
        </div>
    </div>
</header>
```

- [ ] **Step 3: Run the render test to verify the failure moves to CSS or JS**

Run:

```bash
npm run test:site
```

Expected: FAIL, but now the failure should report missing CSS selectors or JS hook rather than missing `reader-layout` or `book-sidebar-shell`.

- [ ] **Step 4: Commit the template update**

```bash
git add theme/index.hbs
git commit -m "feat: rebuild mdbook reader shell"
```

### Task 3: Rebuild The CSS Geometry Around Sidebar + Main + Outline

**Files:**
- Modify: `theme/custom.css`
- Test: `scripts/test-site-render.sh`

- [ ] **Step 1: Replace the incorrect content grid with the correct two-column reader layout**

Update `theme/custom.css` so `#mdbook-content` becomes a right-hand two-column layout and the real mdBook sidebar gets the prototype-like styling. Add or replace the relevant blocks with:

```css
.content {
  padding: 0 0 3rem;
  background: #ffffff;
}

.reader-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(14rem, 17rem);
  gap: clamp(1.5rem, 2.5vw, 2.5rem);
  align-items: start;
  width: min(100%, calc(100vw - var(--sidebar-width)));
  margin: 0;
  padding: 2.25rem clamp(1.5rem, 2.5vw, 2.75rem) 3rem;
}

.reader-main {
  min-width: 0;
  max-width: 100%;
}

.reader-article {
  max-width: 62rem;
  margin: 0;
  padding: 0;
  border: 0;
  background: transparent;
  box-shadow: none;
}

.reader-outline {
  position: sticky;
  top: calc(var(--menu-bar-height) + 1.25rem);
  align-self: start;
}
```

Update the sidebar shell so it matches the prototype instead of the current default mdBook appearance:

```css
.book-sidebar-shell {
  width: clamp(18rem, 22vw, 21rem);
  background: #f8fafc;
  border-inline-end: 1px solid rgba(30, 41, 59, 0.08);
  box-shadow: none;
}

.book-sidebar-shell .chapter {
  padding: 1rem 1rem 2rem;
  font-size: 0.875rem;
}

.book-sidebar-shell .chapter li.part-title {
  margin-top: 1.5rem;
  margin-bottom: 0.4rem;
  color: #64748b;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.12em;
}

.book-sidebar-shell .chapter li a.active {
  background: #3467e8;
  color: #ffffff;
}
```

- [ ] **Step 2: Simplify the header and article visuals so content dominates**

Replace the heavier shell styles with a more prototype-like reading surface:

```css
#mdbook-menu-bar {
  background: rgba(255, 255, 255, 0.96);
  border-block-end: 1px solid rgba(30, 41, 59, 0.08);
  backdrop-filter: blur(10px);
}

.book-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: min(100%, calc(100vw - var(--sidebar-width)));
  margin: 0;
  min-height: 4rem;
  padding: 0 1.5rem;
}

.book-home-link {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
}

.book-home-label {
  color: #1e293b;
  font-size: 0.95rem;
  font-weight: 500;
}

.content h1 {
  margin-top: 0;
  padding-bottom: 0;
  border-bottom: 0;
  font-size: clamp(3rem, 4vw, 4.25rem);
  line-height: 1.02;
}
```

Update the typography and table rules so the chapter page matches the prototype’s rhythm:

```css
.content main {
  font-size: 1rem;
  line-height: 1.75;
}

.content p {
  max-width: 58rem;
  margin-bottom: 1.35rem;
}

.content h2 {
  margin-top: 3.5rem;
  margin-bottom: 1rem;
  font-size: clamp(2rem, 2.5vw, 2.5rem);
}

.content table {
  width: min(100%, 62rem);
  margin: 2rem 0;
  overflow-x: auto;
}
```

- [ ] **Step 3: Add responsive rules that preserve the real sidebar and drop the outline first**

Update the responsive section to:

```css
@media (max-width: 1280px) {
  .reader-layout {
    grid-template-columns: minmax(0, 1fr);
  }

  .reader-outline {
    display: none;
  }
}

@media (max-width: 1080px) {
  .book-toolbar,
  .reader-layout {
    width: 100%;
  }
}

@media (max-width: 760px) {
  .content {
    padding-bottom: 2rem;
  }

  .reader-layout {
    padding: 1.5rem 1rem 2rem;
  }

  .content h1 {
    font-size: clamp(2.2rem, 9vw, 3rem);
  }

  .chapter-pagination {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 4: Run the render test to verify the CSS is now the source of truth**

Run:

```bash
npm run test:site
```

Expected: FAIL only if the JS hook or a selector typo is still missing. It should not fail for the removed fake-left-column model anymore.

- [ ] **Step 5: Commit the CSS rewrite**

```bash
git add theme/custom.css
git commit -m "feat: align mdbook reader geometry to prototype"
```

### Task 4: Trim The JS To DOM Glue And Verify The Real Output

**Files:**
- Modify: `theme/custom.js`
- Test: `scripts/test-site-render.sh`

- [ ] **Step 1: Keep only the DOM glue needed for the outline rail and progress**

Update `moveOutline()` in `theme/custom.js` so it marks completion after moving the generated `On This Page` block:

```js
function moveOutline() {
  const outlineBody = document.querySelector(".book-outline-body");
  const onThisPage = document.querySelector(".on-this-page");

  if (!outlineBody || !onThisPage || onThisPage.parentElement === outlineBody) {
    return;
  }

  outlineBody.replaceChildren(onThisPage);
  document.body.classList.add("book-outline-ready");
}
```

If the existing wheel interception and internal-scroll bridge are no longer required after the layout rewrite, delete those sections instead of preserving them. The final JS file should retain only code necessary for:

- `moveOutline()`
- progress updates against the actual scroller
- stable hash-link positioning if the remaining layout still needs it

- [ ] **Step 2: Run the render test and verify it passes**

Run:

```bash
npm run test:site
```

Expected: PASS with `Site render checks passed.`

- [ ] **Step 3: Run the full build and verify the generated shell markers**

Run:

```bash
npm run build
```

Expected: PASS with generated output under `book/`.

Then verify the generated HTML contains the corrected reader model:

```bash
grep -q 'class="reader-layout"' book/index.html
grep -q 'class="reader-main"' book/index.html
grep -q 'class="reader-outline"' book/index.html
grep -q 'class="book-sidebar-shell"' book/index.html
grep -q 'class="reader-layout"' book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html
```

Expected: all five commands exit `0`.

- [ ] **Step 4: Commit the JS and final verification changes**

```bash
git add theme/custom.js scripts/test-site-render.sh theme/index.hbs theme/custom.css
git commit -m "feat: finish corrected book reader alignment"
```
