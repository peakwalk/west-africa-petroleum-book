# Landing And Book Redesign Design

**Date:** 2026-05-31

**Goal**

Align the public landing page and the mdBook reading experience with the approved `temp/figma-prototype` design language while preserving the existing Markdown authoring flow and static site deployment model.

**Context**

The current site uses two rendering paths:

- `index.html` + `assets/css/landing.css` for the landing page
- `src/**/*.md` + `book.toml` + mdBook theme overrides for the book

The prototype reference lives in:

- `temp/figma-prototype/src/app/pages/HomePage.tsx`
- `temp/figma-prototype/src/app/pages/ReadingPage.tsx`

The prototype is a visual reference, not a runtime target. We will port its structure, spacing, palette, and component treatment into the existing static site.

## Scope

In scope:

- Replace the landing page structure and styling so it visually follows the prototype home page
- Replace the mdBook reading shell so the book layout follows the prototype reading page
- Keep the existing chapter content, build commands, public output structure, search index, print support, and repository links

Out of scope:

- Converting the site to React or Vite
- Implementing prototype-only routes such as `/search`, `/chapters`, `/countries`, or `/fiscal`
- Rewriting chapter content to match the sample copy in the prototype

## Design Decisions

### 1. Landing page stays static

The landing page remains a hand-authored HTML file so the build pipeline stays minimal. The page will adopt the prototype layout:

- sticky top navigation with logo and primary links
- image-backed hero with two calls to action
- audience card grid
- chapter structure preview cards
- simple footer with brand and utility links

The landing page will link into `book/` instead of prototype-only routes.

### 2. mdBook remains the content engine

The book continues to be generated from `src/**/*.md` using mdBook. Only the rendered shell changes.

We will move from light-touch `additional-css` styling to a fuller mdBook theme override so we can control:

- toolbar layout
- left navigation presentation
- right-side "On This Page" rail
- chapter progress bar
- previous/next navigation cards
- content column spacing and typography

### 3. One visual system across landing and book

Both surfaces will share the same visual language:

- primary blue with warm orange accent
- serif display headings and sans-serif body text
- soft neutral backgrounds
- rounded cards and subtle borders
- generous vertical spacing

The implementation may not use the exact prototype CSS classes, but the rendered result should feel recognizably the same.

## Architecture

### Landing page

- `index.html` becomes the single source of landing markup
- `assets/css/landing.css` becomes the complete landing style layer
- existing GA script stays in place

### Book page

- `book.toml` keeps using the HTML renderer
- `theme/index.hbs` becomes the custom mdBook shell
- `theme/book.js` provides shell behavior that must integrate with mdBook runtime behavior
- `theme/custom.css` remains the book stylesheet entry point for typography, layout, colors, and responsive behavior
- `theme/custom.js` can keep the internal scroll bridge if still needed, but the final shell should avoid fighting mdBook defaults unnecessarily

## Behavior Requirements

### Landing page

- Must remain fully static and work from document-relative asset paths
- Must preserve mobile navigation behavior
- Primary CTA goes to `book/`
- Secondary CTA goes to an anchored book structure section, not a missing route

### Book page

- Left table of contents remains driven by `SUMMARY.md`
- Search, theme switcher, print link, repository link, and edit link remain available
- Header navigation list in the sidebar remains functional
- The reading shell must work on desktop and mobile
- Chapter content from Markdown must remain untouched and readable without custom per-chapter markup

## Risks And Mitigations

- mdBook theme overrides can drift from upstream defaults.
  Mitigation: override only the files needed for layout control and keep renderer features intact.

- Prototype layouts reference content blocks that do not exist in the real chapters.
  Mitigation: reuse the shell and typography from the prototype, not its sample article body.

- The current custom scroll bridge may conflict with a new shell.
  Mitigation: reevaluate it after the new layout is in place and keep only the minimum behavior required for stable scrolling and hash navigation.

## Acceptance Criteria

- `index.html` visually matches the approved prototype home page direction
- `book/` renders with a reading shell visually aligned to the prototype reading page
- `npm run build` succeeds
- `public/index.html` and `public/book/**/*.html` are generated successfully
- Existing Markdown content remains navigable and searchable
