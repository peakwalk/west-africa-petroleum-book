## 1. Homepage content model and routing contract

- [ ] 1.1 Add a repo-owned structured homepage content source for country metadata, country routes, topic destinations, latest updates, footer coverage, and shared homepage strings.
- [ ] 1.2 Normalize homepage route helpers so country cards, the West Africa map, topic cards, search entry points, and contact actions all resolve through one maintained source of truth.

## 2. Shared shell and hero redesign

- [ ] 2.1 Update the shared landing shell and top navigation to remove obsolete `Resources` and `About` entries, keep `Countries` and `Chapters`, add `Search` and `Contact`, wire the section-targeting and contact behavior, and preserve locale-safe behavior in both editions.
- [ ] 2.2 Implement the revised hero and homepage section order for the English homepage, including the updated positioning and current-edition entry point.

## 3. Discovery surfaces and trust modules

- [ ] 3.1 Implement the `Coverage Across West Africa` section as 16 uniform country cards with status, ministry/NOC metadata, scale metrics, and chapter-3 deep links.
- [ ] 3.2 Implement a clickable West Africa political map that routes to the same country destinations as the country cards.
- [ ] 3.3 Replace `Explore the Reference Library` with `Browse by Topic` using the approved topic destinations from the Version 2 material.
- [ ] 3.4 Add `Search Upstream Atlas` as a book-only search entry that reuses the existing mdBook search surface.
- [ ] 3.5 Replace the homepage authors module with `Latest Updates`, keep `Current Edition`, simplify `Future Development`, and expand footer coverage/contact messaging.

## 4. Verification and phased rollout

- [ ] 4.1 Update site-render assertions and targeted tests for the new shared shell, section order, country targets, topic targets, search entry, and contact action.
- [ ] 4.2 Run `npm run build:site` and `npm run test:site`, then manually inspect representative English and French homepage outputs.
- [ ] 4.3 Confirm that the English homepage ships the full Version 2 body redesign while the French homepage remains functional and free of broken shared-shell links.
