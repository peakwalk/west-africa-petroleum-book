## Context

`scripts/shared/homepage-content.mjs` holds the `COUNTRIES` metadata and renders the English homepage country cards. Each English card presently has a stable chapter URL and fragment but shares the visible label “Country Analysis”. The generated `public/` site is a build artifact and must not be edited directly.

UA-14 supplies the published English edition's 16 country-to-chapter mappings. The French compatibility homepage does not render this card collection and points to a differently structured chapter, so it is not part of this change.

## Goals / Non-Goals

**Goals:**

- Make every English country-card link visibly identify its published `Chapter 3.X` location.
- Preserve the existing URL, fragment, markup classes, typography, colour, hover behaviour, and responsive rules.
- Make the full 16-item label-and-destination contract machine-verifiable from generated HTML.

**Non-Goals:**

- Changing the English chapter content, anchors, or country order.
- Altering French homepage navigation or translating the English `Chapter` label.
- Adding CSS, JavaScript dependencies, URL redirects, or a runtime data source.

## Decisions

### Keep the chapter number as explicit country metadata

Each English country record will receive a `chapterNumber` value such as `3.1`, rendered as `Chapter ${chapterNumber} →`.

This keeps editorial link text next to the existing country name and anchor, is easy to audit against the published edition, and does not depend on parsing opaque HTML-anchor strings. Deriving the number from anchors was rejected because the anchor format is a routing identifier, not an editorial chapter-number contract. A separate mapping object was rejected because it would split a single card's metadata across two locations.

### Limit the renderer change to the English path

The English render branch will use the country metadata for its label. The French branch retains its current compatibility label and destination logic.

This directly matches UA-14's published-English-edition constraint while avoiding an accidental cross-edition change.

### Verify rendered behaviour rather than source-string presence alone

The country-card test will generate a fresh homepage and capture each card's country name, analysis-link text, and `href`. It will assert all 16 expected triples.

This verifies the user-facing result and catches missing entries, wrong labels, reordered mappings, and changed destinations. The site-render script will update its representative static assertion to reject reliance on the obsolete card label.

## Risks / Trade-offs

- **A later editorial change updates an anchor or chapter number independently.** → The complete label-and-href mapping test fails until both metadata values are reviewed together.
- **A text-only change could unexpectedly wrap at a narrow viewport.** → No CSS or markup dimensions change, the new labels are not longer than the old one, and the completed change will be checked at desktop, tablet, and mobile widths.
- **The generated public file could be edited instead of source.** → Only the generator source and tests are changed; `npm run build:site` regenerates output for validation.

## Migration Plan

1. Build the site from the updated source and deploy it through the normal static-site release process.
2. No data or URL migration is required.
3. If rollback is necessary, restore the prior English render label and its tests, then rebuild the site; existing links remain valid throughout.

## Open Questions

None. UA-14 provides the complete English mapping and explicitly excludes URL changes.
