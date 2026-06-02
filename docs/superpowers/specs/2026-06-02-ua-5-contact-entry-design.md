# UA-5 Contact Entry Design

**Date:** 2026-06-02

**Goal**

Add a consistent top-level contact entry across the Upstream Atlas site by exposing a mailto-based email icon in every real header surface that exists in this repository.

**Context**

The Jira request for `UA-5` asks for an email icon in the website header. The current repository does not have a user avatar or account area. It does have two independent header systems:

- the shared landing header used by `/` and `/chapters/`
- the mdBook toolbar used by `/book/**`

If the email entry is added to only one of these systems, the feature becomes inconsistent as soon as the user moves from the landing surface into the reading experience.

## Scope

In scope:

- Add an email icon entry to the shared landing header
- Add a matching email icon entry to the mdBook toolbar
- Use `mailto:matt@operatorassetexchange.com?subject=Upstream%20Atlas`
- Preserve responsive behavior on desktop, tablet, and mobile
- Preserve keyboard accessibility and screen-reader labeling
- Add static regression coverage to the site render test harness

Out of scope:

- Adding a user avatar or account area
- Creating a contact form
- Introducing JavaScript behavior for the contact action
- Adding analytics or event tracking
- Changing the destination email address beyond the Jira-approved target

## Design Decisions

### 1. Treat the feature as a global contact affordance

The first-principles requirement is not "render an icon beside an avatar." It is "make contacting the team easy from the site header." Because the repository has two actual header implementations, both must expose the contact action.

### 2. Use native mailto behavior

The simplest, most robust implementation is a semantic anchor:

`mailto:matt@operatorassetexchange.com?subject=Upstream%20Atlas`

This delegates email-client behavior to the browser and operating system, which is the standard industry practice for a lightweight contact affordance.

### 3. Keep the action icon-only but accessible

The action should be visually compact to fit the current header density, but it must still be fully accessible:

- `aria-label="Contact Us"`
- keyboard focus styling
- visible hover/focus hint on landing surfaces
- touch target sized for mobile interaction

### 4. Preserve current responsive information architecture

On landing surfaces, the current layout collapses below `900px` by hiding the primary nav and CTA while keeping the mobile menu trigger. The contact action should stay visible during that collapse so the user keeps a one-tap contact path on smaller screens.

### 5. Reuse existing visual language

No new icon library or design subsystem should be introduced. The landing header already uses custom inline SVG in generated markup, and the mdBook toolbar already uses its icon-button treatment. UA-5 should extend these patterns instead of inventing a third one.

## Architecture

### Landing header

- Source of truth: `scripts/shared/landing-shell.mjs`
- Style layer: `assets/css/landing.css`
- A new `header-actions` cluster will own the contact action and CTA
- The mobile menu remains the existing `<details>`-based navigation control

### Book toolbar

- Source of truth: `theme/index.hbs`
- Style layer: `theme/custom.css`
- The new contact entry will live in `toolbar-right` next to the existing search and repository actions

### Verification

- Static regression harness: `scripts/test-site-render.sh`
- Generated outputs inspected through `public/index.html`, `public/chapters/index.html`, and `public/book/index.html`

## Behavior Requirements

### Landing surfaces

- Display the email icon in the header on `/` and `/chapters/`
- Keep the icon visible at desktop, tablet, and mobile widths
- Show the `Contact Us` label on hover or keyboard focus
- Open the default mail client with recipient and subject populated

### Book surfaces

- Display the email icon in the book toolbar on `/book/**`
- Keep the control visually aligned with the existing icon-button system
- Open the default mail client with the same recipient and subject

## Risks And Mitigations

- `mailto:` behavior depends on the user's OS and browser configuration.
  Mitigation: keep the implementation to a standard anchor and verify the generated href exactly.

- Adding another header control could disturb the current mobile collapse.
  Mitigation: place the control in an explicit `header-actions` wrapper and add breakpoint rules that preserve current menu behavior.

- The landing and mdBook headers could drift visually if styled independently.
  Mitigation: reuse the existing control shapes and color tokens instead of inventing separate styling logic.

## Acceptance Criteria

- Landing and chapter pages render a visible email icon in the header
- Book pages render a visible email icon in the toolbar
- Every email icon uses `mailto:matt@operatorassetexchange.com?subject=Upstream%20Atlas`
- Landing surfaces expose a `Contact Us` hover/focus hint
- `npm run test:site` passes with new assertions for all three generated surfaces
