# Book Reading UI Alignment Design

**Date:** 2026-05-31

**Goal**

Align the mdBook reading interface at `/book/` to the approved `figma-prototype` reading page while preserving mdBook's existing interaction model, content pipeline, and build process.

**Reference Material**

- Prototype source: `temp/figma-prototype/src/app/pages/ReadingPage.tsx`
- Prototype theme tokens: `temp/figma-prototype/src/styles/theme.css`
- Prototype deployment: `https://candy-zebra-72648958.figma.site/read`
- Current reading shell: `theme/index.hbs`
- Current reading styles and behavior: `theme/custom.css`, `theme/custom.js`

## Context

The current `/book/` experience already contains most of the required information architecture:

- a sticky top toolbar
- a left chapter navigation rail
- a central reading column
- a right-side "On This Page" rail
- a reading progress indicator
- previous and next chapter navigation

The gap is not architectural. The gap is layout fidelity, spacing, density, component treatment, and the overall reading-shell polish relative to the approved prototype.

This work should therefore avoid a rewrite. The correct strategy is to reshape the existing mdBook shell so it renders like the prototype without discarding mdBook behavior.

## Scope

In scope:

- the `/book/` reading interface shell
- the sticky header layout and styling
- the left chapter navigation presentation
- the center reading column layout and typography treatment
- the right "On This Page" rail presentation
- the reading progress bar treatment
- the previous/next chapter card styling
- responsive behavior for the reading shell only

Out of scope:

- landing page redesign
- search page redesign
- `toc.html` or chapter index page redesign
- `print.html` redesign
- changing chapter content or Markdown structure
- introducing new routes from the prototype such as `/search`, `/chapters`, `/countries`, or `/fiscal`
- porting the prototype runtime from React/Vite into this project

## Constraints

The implementation must preserve the following:

- mdBook remains the content engine
- chapter content continues to come from `src/**/*.md`
- left navigation remains generated from `SUMMARY.md`
- right-side section navigation remains generated from chapter headings
- search, theme toggle, print, repository link, and edit link keep their existing behaviors
- current build commands remain valid

The implementation must not require direct edits to generated output inside `book/` or `public/book/`.

## Design Decisions

### 1. Preserve mdBook behavior, replace only the shell treatment

The project will keep mdBook's semantics, ids, generated content hooks, and control behavior. We will not attempt to reconstruct the reading experience as a React page.

Instead, we will:

- keep `theme/index.hbs` as the shell entry point
- keep `theme/custom.css` as the primary styling layer
- keep `theme/custom.js` only for light DOM wiring and scroll-related enhancements

This keeps risk low while still allowing high visual fidelity.

### 2. Match the prototype's reading mental model

The prototype establishes a clear reading-shell model:

- compact sticky toolbar
- always-present left chapter rail on desktop
- centered reading card
- quiet right auxiliary rail for in-page navigation
- thin progress line
- lightweight chapter-to-chapter cards

The mdBook page will adopt the same model, even if the underlying DOM differs.

### 3. Keep content-driven navigation, not prototype stub data

The prototype uses hard-coded chapter and table-of-contents arrays. The production book cannot do that. It must continue to reflect actual book content.

Therefore, fidelity is defined as:

- same layout hierarchy
- same visual density
- same card and panel treatment
- similar spacing and typography rhythm

Fidelity is not defined as copying the prototype's placeholder data or route system.

## Proposed Implementation

### Files to change

- `theme/index.hbs`
- `theme/custom.css`
- `theme/custom.js`

### `theme/index.hbs`

Make only small structural changes, keeping mdBook integration points intact.

Expected structure after update:

- header with three regions
  - left: sidebar toggle and brand link
  - center: reading context label and book title
  - right: mdBook action buttons
- progress bar directly below the header
- three-column content shell
  - left sidebar: mdBook-generated chapter navigation
  - center main area: article card plus chapter pagination
  - right sidebar: moved "On This Page" content

The template will not change:

- `{{{ content }}}`
- search container ids and controls
- theme switcher ids and controls
- sidebar container ids
- previous/next chapter data usage

### `theme/custom.css`

This file will become the primary source of fidelity.

Required styling outcomes:

- top toolbar visually matches the prototype's compact reading bar
- toolbar buttons share consistent icon-button sizing and hover treatment
- toolbar center regains prominence on desktop and collapses cleanly on smaller widths
- chapter rail reads as a structured navigation surface, not raw mdBook defaults
- active chapter uses the primary solid highlight
- chapter groups use quieter, compact label styling
- right rail looks like a supportive panel rather than a second primary column
- article content becomes the visual center through a white card, soft border, larger padding, and subtle shadow
- headings, body text, tables, blockquotes, and media use spacing that matches the prototype's reading cadence
- progress bar becomes thinner and more understated
- previous/next cards become lighter, denser, and closer to the prototype's composition

### `theme/custom.js`

The JavaScript remains minimal and supports the shell rather than defining it.

It should continue to handle:

- internal scrolling bridge if still required by the custom layout
- moving the generated "On This Page" block into the right rail container
- updating the reading progress bar against the actual scroll container
- stable hash-link scrolling within the internal scroll container

If any of the current bridge behavior is unnecessary after the CSS and template updates, it should be removed instead of preserved out of habit.

## Responsive Strategy

Desktop fidelity is the priority, but responsiveness must remain solid.

### Large desktop

At wide widths, the page should present the full three-column reading layout:

- left navigation rail visible
- center reading card with stable max width
- right "On This Page" rail visible

This is the closest match to the prototype.

### Medium widths

At medium widths, the right rail can collapse away first to preserve reading width. The left rail remains available because it is still the main navigation tool.

### Narrow widths and tablet

The left rail remains toggleable rather than permanently visible. The center content shifts to a single reading column, while the header becomes denser and stacks only where necessary.

### Mobile

The reading column becomes fully single-column:

- tighter page padding
- reduced article padding
- scaled-down heading sizes
- pagination cards stacked vertically
- right rail hidden

The result should still feel like the same product, not a separate mobile design.

## Risks And Mitigations

### Risk: mdBook default styles fight the custom shell

Mitigation:

- override only reading-shell selectors intentionally
- preserve mdBook ids and containers
- avoid broad resets that impact unrelated generated pages

### Risk: internal scroll handling breaks hash navigation or progress tracking

Mitigation:

- keep progress and anchor behavior tied to the actual scroll container
- test direct hash navigation and in-page heading jumps
- remove unnecessary bridge code if layout can operate without it

### Risk: content-heavy chapters expose overflow issues

Mitigation:

- preserve horizontal overflow handling for tables
- keep image max-width constraints
- test at least one long chapter and one table-heavy chapter

## Acceptance Criteria

- `/book/` visually aligns with the approved prototype reading page direction
- the page retains mdBook interactions for sidebar toggle, search, theme switching, print, repository, and edit actions
- the left navigation, center reading card, and right "On This Page" rail read as a cohesive three-column reading shell on desktop
- the reading progress bar updates correctly during scroll
- previous/next chapter navigation remains functional
- responsive behavior remains usable on tablet and mobile widths
- `npm run build` succeeds without requiring manual edits to generated output

## Validation Plan

1. Update the template, CSS, and JS in the theme source.
2. Run the existing build command.
3. Inspect at least one long-form chapter and one table-heavy chapter.
4. Verify:
   - header layout
   - sidebar toggle
   - search control visibility and behavior
   - theme toggle behavior
   - right-rail section list placement
   - progress bar updates
   - previous/next chapter links
5. If visual confirmation is needed, compare a local reading page screenshot against the deployed prototype using Playwright screenshots.
