# UA-8 Remove Git Repository Entry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the public Git repository icon and link from the Upstream Atlas reading experience and prevent regressions that would re-expose source repository URLs.

**Architecture:** Treat the repository entry as a static-output contract problem, not a cosmetic one. First lock the failure into `scripts/test-site-render.sh`, then remove the repository anchor from the mdBook toolbar template and clear repository-related HTML config in `book.toml`, and finally re-run the full site render verification against generated output.

**Tech Stack:** mdBook Handlebars template, TOML configuration, shell-based static regression checks, npm build scripts

---

### Task 1: Lock The Regression In Static Tests

**Files:**
- Modify: `scripts/test-site-render.sh`
- Inspect: `theme/index.hbs`
- Inspect: `book.toml`

- [ ] **Step 1: Add failing negative assertions for repository UI and URLs**

```sh
check_not_contains public/book/index.html 'title="Git repository"'
check_not_contains public/book/index.html 'https://github.com/peakwalk/west-africa-petroleum-book'
check_not_contains public/book/print.html 'title="Git repository"'
check_not_contains public/book/404.html 'title="Git repository"'
check_not_contains public/book/chapters/front-matter.html 'title="Git repository"'
check_not_contains public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'title="Git repository"'
```

- [ ] **Step 2: Run the site render regression and verify it fails for the right reason**

Run: `scripts/test-site-render.sh`
Expected: FAIL because the current generated book pages still include the repository anchor and GitHub URL.

### Task 2: Remove The Repository Entry At The Source

**Files:**
- Modify: `theme/index.hbs`
- Modify: `book.toml`

- [ ] **Step 1: Remove the conditional Git repository anchor from the toolbar template**

```hbs
{{#if search_enabled}}
<button id="mdbook-search-toggle" class="icon-button" type="button" title="Search (`/`)" aria-label="Toggle Searchbar" aria-expanded="false" aria-keyshortcuts="/ s" aria-controls="mdbook-searchbar">
    {{fa "solid" "magnifying-glass"}}
</button>
{{/if}}
<a class="icon-button toolbar-link toolbar-contact-link" href="mailto:matt@operatorassetexchange.com?subject=Upstream%20Atlas" title="Contact Us" aria-label="Contact Us">
    {{fa "solid" "envelope"}}
</a>
```

- [ ] **Step 2: Remove repository-related public HTML config so future template changes cannot rehydrate the link**

```toml
[output.html]
theme = "theme"
default-theme = "light"
preferred-dark-theme = "navy"
additional-css = ["theme/custom.css"]
additional-js = ["theme/ga.js", "theme/custom.js"]
site-url = "/west-africa-petroleum-book/book/"
no-section-label = true
```

### Task 3: Verify The Removal End To End

**Files:**
- Inspect: `public/book/index.html`
- Inspect: `public/book/print.html`
- Inspect: `public/book/404.html`

- [ ] **Step 1: Re-run the full site render regression**

Run: `scripts/test-site-render.sh`
Expected: PASS with no repository UI present in generated book output.

- [ ] **Step 2: Search generated output for any remaining public repository reference**

Run: `rg -n 'title="Git repository"|https://github.com/peakwalk/west-africa-petroleum-book' public/book`
Expected: No matches.
