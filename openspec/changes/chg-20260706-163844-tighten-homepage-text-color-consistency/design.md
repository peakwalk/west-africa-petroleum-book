## Context

The current landing styles already define a partial homepage palette in `assets/css/landing.base.css`, including `--homepage-heading-text`, `--homepage-primary-text`, `--brand-blue`, and `--brand-blue-deep`. However, the white-surface homepage modules still mix additional hard-coded values such as `#17346f`, `#244da3`, `#2f56a4`, `#2f67f6`, `#4a5d78`, `#61708a`, and `#7287b3` for roles that are visually very close.

That drift now shows up most clearly across header navigation, the stakeholder strip, country cards, search chips, topic cards, and the closing summary row. The approved homepage information architecture and section composition do not need another redesign; the gap is that descriptive text often looks almost as emphasized as interactive text, while different interactive elements no longer share one obvious link color.

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

### Decision: Keep the change CSS-only unless verification reveals a generated-file dependency
The target problem lives in the homepage styles rather than content or generated HTML structure. The implementation will stay CSS-only unless a verification failure shows that a generated output or test fixture must also be refreshed.

Alternative considered:
- Regenerate homepage HTML preemptively as part of the style cleanup. Rejected because no planned change requires markup changes.

## Risks / Trade-offs

- [Reducing blue emphasis too aggressively could make some cards feel flatter than the approved reference] -> Keep headings and entity labels on stronger homepage blues while moving only explanatory text toward calmer body/meta roles.
- [Link-color unification could reduce the visual prominence of a few previously brighter CTAs] -> Keep one shared default link role and a darker hover role, then verify the major CTAs still read as actionable in context.
- [Responsive overrides may still carry old hard-coded colors] -> Review tablet and mobile homepage CSS for any text-role leftovers after the desktop role cleanup.
- [The repo already has recent homepage OpenSpec changes in adjacent areas] -> Keep this change scoped to text-color hierarchy only so it composes cleanly with the earlier search, topic, map, and stakeholder changes.

## Migration Plan

1. Record the narrow text-color-consistency scope in OpenSpec artifacts and Chinese companions.
2. Consolidate homepage white-surface text roles in `landing.base.css`.
3. Update homepage module CSS to use the shared text roles instead of one-off near-duplicate blues.
4. Run the narrowest relevant verification for homepage rendering and styling.
5. If the result over-corrects the approved visual balance, roll back the color-role assignments without touching layout or content artifacts.

## Open Questions

- None. The user has already approved continuing with the text-color consistency plan after the audit.
