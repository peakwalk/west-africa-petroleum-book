## Context

The current landing styles already define a partial homepage palette in `assets/css/landing.base.css`, including `--homepage-heading-text`, `--homepage-primary-text`, `--brand-blue`, and `--brand-blue-deep`. However, the white-surface homepage modules still mix additional hard-coded values such as `#17346f`, `#244da3`, `#2f56a4`, `#2f67f6`, `#4a5d78`, `#61708a`, and `#7287b3` for roles that are visually very close.

That drift now shows up most clearly across header navigation, the stakeholder strip, country cards, search chips, topic cards, and the closing summary row. The approved homepage information architecture and section composition do not need another redesign; the gap is that descriptive text often looks almost as emphasized as interactive text, while different interactive elements no longer share one obvious link color.

A second screenshot comparison against the approved composition also showed a narrower issue inside the white-surface modules: the first cleanup pushed some content-bearing sublabels and empty-state lines too far toward the metadata role, while shared CTAs and chip-like controls became consistent but a little too quiet. The next pass therefore needs to preserve consistency without making those sections feel lighter or sparser than the reference.

A third screenshot comparison narrowed the remaining mismatch further. The page-wide hierarchy is now broadly correct, but the country grid, topic cards, and closing summary row still read slightly lighter and less compact than the approved reference. The next refinement pass should therefore focus on text density and card presence inside those three module groups instead of reopening the broader homepage hierarchy.

The user has also now supplied a specific hero-stat icon source set at `design_replicated_icons_v10`. That request is not about hierarchy tuning; it is a direct asset-alignment step for the six hero metrics, and it should be implemented through the existing hero icon asset hooks rather than by rebuilding the hero metric markup.

The user has now also supplied a `topic-card` icon source set at `oil_icons_v8_thicker_third_icon`. Its review notes explicitly call out one narrow follow-up adjustment: only the third icon, `National Oil Companies`, was thickened further, while the other five stay on the previously approved v7 shapes. That means the homepage topic icons should continue to consume the supplied SVG assets directly instead of trying to redraw those shapes as inline vector paths or relying on browser-side downscaling of large PNG exports.

## Goals / Non-Goals

**Goals:**
- Define one consistent homepage text hierarchy for white-surface sections: headings, emphasis/entity text, supporting body copy, metadata, and interactive text.
- Replace module-specific near-duplicate text blues with a smaller shared set of role-based homepage tokens or role assignments.
- Restore clearer distinction between descriptive copy and clickable text in cards, strips, search chips, and section-level CTAs.
- Keep changes narrow enough that the current layout, spacing, typography scale, routes, and localized copy remain intact.

**Non-Goals:**
- Redesign the homepage layout, section order, or card composition.
- Rework hero imagery, footer structure, iconography, or content strategy.
- Introduce a new global brand palette for the whole book reader.
- Change copy, destinations, or any backend behavior associated with homepage search or navigation.

## Decisions

### Decision: Add explicit homepage body, metadata, and link text roles
The homepage already has heading and emphasis blues, but it lacks explicit shared roles for body copy, metadata, and interactive text. This change will add the missing roles in `landing.base.css` so the other homepage styles can stop encoding those roles through scattered one-off hex values.

Alternative considered:
- Reuse only the existing `--homepage-primary-text`, `--brand-blue`, and `--text-muted` values. Rejected because that still leaves metadata and supporting body copy underspecified, which is what caused the current drift.

### Decision: Reserve emphasis blue for entity labels and selected supportive headings, not for most descriptive copy
Descriptive text on white cards and white sections will shift toward a calmer body/meta palette rather than staying on `--homepage-primary-text`. The stronger homepage blues will be kept for headings, entity names, and intentionally emphasized labels where that emphasis is useful.

Alternative considered:
- Keep all homepage descriptive copy in the current medium-blue family and only unify link colors. Rejected because the main issue is not only link inconsistency; it is that too much non-interactive copy currently looks emphasized.

### Decision: Use one shared interactive text baseline across section links, card links, and search chips
White-surface interactive text will use one shared link role by default and one darker hover role, rather than letting individual modules invent adjacent blues. This keeps section CTAs, country links, topic links, summary links, and search chips recognizably related.

Alternative considered:
- Preserve separate CTA/link blues to make each module more distinctive. Rejected because the user's feedback is specifically about perceived inconsistency, and these differences do not communicate meaningful product hierarchy.

### Decision: Reserve metadata for truly quiet helper text, not content-bearing sublabels
Dates, placeholders, and helper labels can stay on the quiet metadata role. By contrast, country abbreviations, no-hydrocarbon messages, and similar content-bearing short lines should stay on the supporting body role so the cards do not look washed out compared with the approved reference.

Alternative considered:
- Keep all secondary one-line text on the metadata role for maximum separation. Rejected because the screenshot comparison showed that this makes the country grid and summary row feel under-inked rather than clearer.

### Decision: Restore CTA and control affordance with weight, size, and border contrast before adding new colors
The next pass will strengthen shared CTAs and chip-like controls through font weight, local size adjustments, and slightly firmer border/shadow treatment. This keeps the interaction family consistent while restoring the sharper clickable feel shown in the approved reference.

Alternative considered:
- Introduce another brighter homepage CTA blue for section links and chips. Rejected because the approved reference can be matched more faithfully by strengthening affordance cues first, without increasing palette complexity.

### Decision: Finish the remaining visual gap through local density tuning in country, topic, and summary cards
The remaining mismatch is no longer about global text-role assignment. Instead, the country cards, topic cards, and summary row need a final local pass on font size, weight, and card shell presence so those sections feel as information-dense and decisive as the approved reference.

Alternative considered:
- Reopen the broader homepage token hierarchy again. Rejected because the latest screenshot comparison shows that the remaining gap is local to a few card groups rather than systemic.

### Decision: Replace hero-stat icon assets in place, keeping the existing hero metric markup and CSS hooks
The homepage hero already renders each stat icon through stable `hero-*.svg` asset references. Because the user supplied a one-to-one replacement icon set, the implementation should swap those six asset files in place and preserve the existing `hero-stat-icon--*` class hooks and markup structure.

Alternative considered:
- Rebuild the hero stat cards around inline `<img>` tags or a new sprite system. Rejected because the request is only to adopt the supplied icon artwork, and the current asset hookup already provides the required replacement seam.

### Decision: Replace topic-card inline SVG paths with static asset-backed images while keeping the existing card classes
The homepage topic cards currently emit small inline SVG path sets from `homepage-topic-reference.mjs`. Because the user supplied a six-icon SVG asset pack whose latest approved revision only thickens the third icon for better small-size weight, the topic icon renderer should switch from inline path markup to `<img>` references under a stable repo asset directory while preserving the `topic-card-icon` and `topic-card-icon--*` class hooks.

Alternative considered:
- Re-vectorize the supplied screenshot-derived icons back into new inline path definitions. Rejected because the source notes explicitly warn that reconstructing vector paths from the screenshot changes shape details, which is the opposite of the user's request.

### Decision: Keep the change CSS-only unless verification reveals a generated-file dependency
The target problem lives in the homepage styles rather than content or generated HTML structure. The implementation will stay CSS-only unless a verification failure shows that a generated output or test fixture must also be refreshed.

Alternative considered:
- Regenerate homepage HTML preemptively as part of the style cleanup. Rejected because no planned change requires markup changes.

## Risks / Trade-offs

- [Reducing blue emphasis too aggressively could make some cards feel flatter than the approved reference] -> Keep headings and entity labels on stronger homepage blues while moving only explanatory text toward calmer body/meta roles.
- [Link-color unification could reduce the visual prominence of a few previously brighter CTAs] -> Keep one shared default link role and a darker hover role, then restore emphasis through weight, size, and local affordance styling before introducing more color variance.
- [Responsive overrides may still carry old hard-coded colors] -> Review tablet and mobile homepage CSS for any text-role leftovers after the desktop role cleanup.
- [The repo already has recent homepage OpenSpec changes in adjacent areas] -> Keep this change scoped to text-color hierarchy only so it composes cleanly with the earlier search, topic, map, and stakeholder changes.
- [Re-promoting content-bearing sublabels could make quiet helper text too loud again] -> Reserve the metadata role only for dates, placeholders, and truly auxiliary labels, then verify the resulting hierarchy against the approved screenshot rather than by selector names alone.
- [Local density tuning could overshoot and make the white cards feel heavy] -> Increase emphasis only by small increments and keep the refinement scoped to the three screenshot-identified module groups.
- [Direct asset replacement could silently drift from the supplied source set if filenames are mapped incorrectly] -> Keep the one-to-one mapping explicit and add a narrow verification that the repo hero icon assets now carry the expected filled-path V10 signature.
- [Switching topic icons from inline SVG to image assets could introduce small alignment or sizing drift inside the cards] -> Keep the existing icon class hooks, constrain the `<img>` through the current fixed icon box, and add a narrow render/assertion check for the generated topic asset references.

## Migration Plan

1. Record the narrow text-color-consistency scope in OpenSpec artifacts and Chinese companions.
2. Consolidate homepage white-surface text roles in `landing.base.css`.
3. Update homepage module CSS to use the shared text roles instead of one-off near-duplicate blues.
4. Re-promote under-emphasized content-bearing short lines from metadata to body where the screenshot comparison shows the current result feels too quiet.
5. Strengthen shared CTA and control affordances through typography and border/shadow treatment while keeping the same interaction family.
6. Apply a final local density pass to country cards, topic cards, and summary cards so their text and card shells match the approved screenshot more closely.
7. Replace the six hero-stat SVG assets in place with the user-supplied V10 set, keeping the current hero markup and CSS references intact.
8. Replace the six topic-card inline icon definitions with references to the user-supplied current approved SVG assets under a stable repo asset path, keeping the topic card layout and class hooks intact.
9. Run the narrowest relevant verification for homepage rendering and styling, including narrow resource-level checks for the hero-stat and topic-card icon replacements.
10. If the result over-corrects the approved visual balance, roll back the color-role assignments without touching layout or content artifacts.

## Open Questions

- None. The user has already approved continuing with the text-color consistency plan after the audit.
