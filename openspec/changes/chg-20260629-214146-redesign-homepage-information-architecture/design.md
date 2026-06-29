## Context

The homepage redesign is driven by the UA-11 Version 2 materials already downloaded into `resources/version2/`, plus the current landing-page implementation in `editions/en/site/index-main.html`, `editions/fr/site/index-main.html`, `scripts/generate-index-page.mjs`, `scripts/shared/landing-shell.mjs`, and `assets/css/landing.css`.

Those materials describe a clearer Version 2 homepage with revised navigation, a country-led exploration layer, a topic-browsing layer, a book-only search layer, and stronger freshness/contact signals. The current homepage does not match that model. It still mixes multiple entry modes, keeps stale top-level navigation items, and does not make country access the dominant exploration surface even though the product is positioned as a West Africa petroleum reference.

From first principles, this homepage only needs to answer five questions:
- What is this reference and why should I trust it?
- Which country can I explore right now?
- Which topic can I explore right now?
- How do I find one specific fact quickly?
- Is the content current, and how do I contact the team?

Those five questions are mutually exclusive and collectively exhaustive for this surface. The redesign should therefore map one clear module or action to each question instead of letting sections overlap or compete.

The repo architecture also constrains the solution. The site is statically generated, the landing pages are repo-owned templates, the book search already exists inside the mdBook reader surface, and chapter 3 already exposes country anchors that country cards can target. The design should exploit those facts instead of introducing a new runtime system.

## Goals / Non-Goals

**Goals:**
- Deliver a homepage information architecture that is obviously organized around orientation, country discovery, topic discovery, book search, and trust/freshness/contact.
- Make country access the primary exploration path for the homepage through 16 uniform country cards and a supplemental West Africa map.
- Reuse existing static book routes, chapter targets, and mdBook search rather than creating a separate search or data backend.
- Replace low-signal homepage elements with higher-signal trust cues such as `Latest Updates`, clearer coverage claims, and direct contact.
- Keep the redesign maintainable by centralizing homepage-controlled data instead of scattering strings and deep links across templates.
- Ship the full body redesign on the English homepage while keeping the French homepage operational through shared shell compatibility.

**Non-Goals:**
- Fully redesign the French homepage body in this change.
- Introduce a dynamic database-backed country-statistics service.
- Build a separate site-wide search experience outside the existing book search surface.
- Change chapter body content, chapter URLs, or the underlying mdBook content model.
- Add hover-detail popups to the map in Phase 1 if they increase implementation risk or mobile complexity.

## Decisions

### Decision: Organize the homepage around five non-overlapping intent zones
The homepage will be structured around five intent zones that directly answer the first-principles questions above:
- orientation: hero, positioning, and current-edition CTA
- country discovery: country cards and geographic map
- topic discovery: `Browse by Topic`
- fact lookup: `Search Upstream Atlas`
- trust and next steps: `Latest Updates`, `Current Edition`, `Future Development`, footer coverage, and contact

This keeps the homepage MECE. Country cards do not compete with topic cards. Search does not masquerade as topic browsing. Latest updates do not repeat author biography content. Footer coverage does not act as a second navigation menu.

Alternative considered:
- Keep the current homepage and only patch individual sections. Rejected because the present problem is structural, not cosmetic; patching sections would preserve the same overlapping mental model.

### Decision: Make country discovery the primary homepage entry path
The homepage will treat country discovery as the main exploration surface because the product promise is geographic petroleum intelligence across West Africa. The `Coverage Across West Africa` section will therefore expose all 16 target countries as uniform cards with consistent sizing, status labeling, ministry/NOC metadata, scale metrics, and a direct CTA into the country subsection inside chapter 3.

The political map is a secondary navigation aid, not a second primary information model. It gives users a geographic shortcut, but it must point to the same country targets as the cards so the system has one source of truth for country routing.

Alternative considered:
- Make the map the primary country-discovery surface and treat cards as optional. Rejected because the map is less legible on mobile and less scannable than a uniform card grid for comparison tasks.

### Decision: Keep topic browsing and search as separate, non-overlapping systems
`Browse by Topic` will provide curated thematic entry points into existing chapters. `Search Upstream Atlas` will provide free-form lookup into the existing book search surface. These two modules solve different problems and should stay distinct.

The redesign will rename `Explore the Reference Library` to `Browse by Topic` and connect the topic cards to the approved chapter destinations in the Version 2 material. The search section will explicitly communicate that it searches the online book only, with no promise of site-wide or external discovery.

Alternative considered:
- Merge topic browsing and search into one generic discovery block. Rejected because curated browsing and exact lookup serve different user intents and produce different expectations.

### Decision: Reuse existing static search and chapter routes
The repo already has canonical book chapter URLs, chapter 3 country anchors, and the mdBook reader search index. The redesign will reuse those surfaces rather than introduce a new search backend or content service. This keeps the implementation consistent with the static build pipeline and avoids creating a second search truth.

Alternative considered:
- Add a new homepage-local search experience backed by a custom dataset. Rejected because it adds runtime complexity without solving a new user problem in Phase 1.

### Decision: Drive homepage content from structured config owned by the repo
The redesign touches data that will evolve independently of layout code: 16 country cards, topic destinations, latest updates, footer coverage claims, and shared shell strings. That information should live in a structured repo-owned content source so templates and scripts render from one canonical dataset.

Alternative considered:
- Hardcode all new homepage content directly in `index-main.html`. Rejected because it makes later content updates fragile and spreads routing truth across markup.

### Decision: Ship the English body redesign first and constrain French impact to shared-shell compatibility
The full homepage structure in the UA-11 Version 2 material is specified in English. This change will therefore deliver the full body redesign for the English homepage while limiting French changes to shared shell, locale-safe routing, and compatibility with the updated architecture. The French homepage must remain functional and must not inherit broken anchors, missing destinations, or English-only shell regressions.

Alternative considered:
- Force a full bilingual homepage redesign in the same change. Rejected because the design direction and approval material are not equally mature for the French body, which would expand scope and risk without helping the English launch path.

### Decision: Implement the map as a clickable baseline and defer richer hover behavior
Phase 1 needs a geographic browsing affordance, but it does not need a complex interactive data application. The baseline map will therefore be a clickable political map that routes to the same country destinations as the cards. Hover popups and auto-generated country statistics remain optional Phase 2 enhancements.

Alternative considered:
- Block the redesign until rich hover popups are ready. Rejected because the user value in Phase 1 is clear country access, not advanced map interactivity.

## Risks / Trade-offs

- [Country metadata can drift from chapter targets] -> Use one structured routing source for cards and map destinations, and verify representative country links in site assertions.
- [The English-first rollout can create EN/FR shell divergence] -> Keep shared navigation, footer actions, and locale-switch behavior under common generation code and verify both editions.
- [Users may expect site-wide search instead of book-only search] -> Label the section explicitly as `Search Upstream Atlas` for the online book and reuse the existing book search destination.
- [A complex map can hurt accessibility and mobile behavior] -> Keep the map secondary to the country cards and require equivalent navigation through the card grid.
- [Latest Updates can become stale if treated like static decoration] -> Keep updates in structured content so they can be revised independently of layout code.

## Migration Plan

1. Add the OpenSpec artifacts for the homepage information architecture and keep the scope boundary explicit.
2. Introduce a structured homepage content source for countries, topics, updates, and footer coverage.
3. Update the shared landing shell, navigation actions, and contact/search wiring.
4. Implement the English homepage body redesign with the new hero, country, topic, search, and trust sections.
5. Keep the French homepage compatible through shared-shell and routing updates without forcing a full body redesign.
6. Update site assertions, build the site, and manually inspect representative English and French homepage outputs.

## Open Questions

- None for this change. The rollout boundary is intentional: English homepage body first, French homepage compatibility now, full French body redesign later if separately approved.
