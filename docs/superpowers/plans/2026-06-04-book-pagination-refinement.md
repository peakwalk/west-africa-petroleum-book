# Book Pagination Refinement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refine the mdBook bottom chapter navigation so it reads as a more editorial, higher-fidelity reading transition rather than two generic CTA cards, including a narrow-screen stacked layout that preserves title readability.

**Architecture:** Keep the existing mdBook previous/next data flow intact, but introduce a richer card substructure in the Handlebars template and restyle that structure in `theme/custom.css`. Preserve the desktop split-card layout while switching narrow screens to a stacked reading flow: `previous` on top and left-aligned, `next` below and right-aligned. Add a regression check that rebuilds the site and asserts the new navigation markup and narrow-screen rules are present.

**Tech Stack:** mdBook, Handlebars template (`theme/index.hbs`), custom CSS, shell-based render verification

---

### Task 1: Add a failing regression check for the new pagination structure

**Files:**
- Create: `scripts/test-book-pagination-render.sh`

- [ ] **Step 1: Write the failing test**

```sh
#!/usr/bin/env sh
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

cd "$ROOT_DIR"
npm run build:site >/dev/null

check_contains() {
  file_path="$1"
  pattern="$2"

  if ! grep -q -- "$pattern" "$file_path"; then
    echo "Missing expected pattern '$pattern' in $file_path" >&2
    exit 1
  fi
}

TARGET="public/book/chapters/glossary.html"

check_contains "$TARGET" 'class="chapter-pagination-eyebrow"'
check_contains "$TARGET" 'class="chapter-nav-arrow"'
check_contains "$TARGET" 'class="chapter-nav-title"'
check_contains "$TARGET" 'class="chapter-nav-meta"'
```

- [ ] **Step 2: Run test to verify it fails**

Run: `sh scripts/test-book-pagination-render.sh`
Expected: FAIL because the generated HTML does not yet contain the new pagination classes.

### Task 2: Implement the refined editorial pagination cards

**Files:**
- Modify: `theme/index.hbs`
- Modify: `theme/custom.css`

- [ ] **Step 1: Update the template structure**

```hbs
<a rel="prev" href="{{ path_to_root }}{{ previous.link }}" class="chapter-nav-card chapter-nav-previous">
    <span class="chapter-pagination-eyebrow">
        <span class="chapter-nav-arrow" aria-hidden="true">←</span>
        <span class="chapter-nav-label">Previous chapter</span>
    </span>
    <strong class="chapter-nav-title">{{ previous.name }}{{ previous.title }}</strong>
    <span class="chapter-nav-meta">Review the prior section</span>
</a>
```

- [ ] **Step 2: Restyle the cards in CSS**

```css
.chapter-nav-card {
  position: relative;
  display: grid;
  gap: 0.8rem;
  padding: 1.2rem 1.25rem 1.15rem;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 1.25rem;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.96) 100%);
}

.chapter-pagination-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
}

.chapter-nav-title {
  font-family: "Lora", Georgia, serif;
  font-size: 1.28rem;
}
```

- [ ] **Step 3: Keep mobile layout readable**

```css
@media (max-width: 760px) {
  .chapter-nav-card {
    padding: 1rem 1rem 0.95rem;
  }

  .chapter-nav-next {
    text-align: left;
  }
}
```

### Task 3: Verify generated output contains the refined markup

**Files:**
- Test: `scripts/test-book-pagination-render.sh`

- [ ] **Step 1: Re-run the focused regression check**

Run: `sh scripts/test-book-pagination-render.sh`
Expected: PASS

- [ ] **Step 2: Re-run the broader site render regression**

Run: `npm run test:site`
Expected: PASS

### Task 4: Rework narrow-screen pagination for stacked readability

**Files:**
- Modify: `theme/custom.css`
- Test: `scripts/test-book-pagination-render.sh`

- [ ] **Step 1: Update the focused regression check to require stacked narrow-screen rules**

```sh
check_not_contains theme/custom.css '.chapter-nav-meta'

NARROW_RULES="$(sed -n '1562,1608p' theme/custom.css)"

printf '%s' "$NARROW_RULES" | grep -q 'flex-direction: column;'
printf '%s' "$NARROW_RULES" | grep -q 'width: 100%;'
printf '%s' "$NARROW_RULES" | grep -q 'text-align: right;'
printf '%s' "$NARROW_RULES" | grep -q 'flex-direction: row-reverse;'
```

- [ ] **Step 2: Make narrow screens stack and restore title width**

```css
@media (max-width: 760px) {
  .chapter-pagination {
    flex-direction: column;
    align-items: stretch;
  }

  .chapter-nav-card {
    width: 100%;
    padding: 14px 16px 14px;
  }

  .chapter-nav-next {
    text-align: right;
  }
}
```

- [ ] **Step 3: Hide the desktop symmetry placeholder in the stacked layout**

```css
@media (max-width: 760px) {
  .chapter-nav-placeholder {
    display: none;
  }
}
```
