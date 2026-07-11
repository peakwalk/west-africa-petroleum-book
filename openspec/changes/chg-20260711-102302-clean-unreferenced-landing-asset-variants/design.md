## Context

After the earlier landing cleanup passes, the remaining `assets/images/` directory still includes several historical hero experiments, a retired map inset asset, and older brand/overlay variants that no current runtime surface consumes. A repository-wide scan found no references to these files in generated landing HTML, generated landing CSS, landing scripts, or the current reader shell.

The public build still publishes them because `scripts/build_site.mjs` copies the entire `assets/` tree into both locale outputs. The candidate set adds up to about `1.41MB` in source and about `2.83MB` across the two built public asset trees.

The one boundary that should stay explicit is the book-theme pagination chain. `prototype-hero-graywhite-left.webp` and `prototype-hero-graywhite-right.webp` are still referenced by `theme/custom.css`, and their retained PNG backups should remain out of scope for this pass.

## Goals / Non-Goals

**Goals:**
- Remove only historical asset variants with no runtime references.
- Keep active landing assets and book-theme pagination assets untouched.
- Add regression coverage so the deleted variants stay absent from both source and built trees.

**Non-Goals:**
- Change the landing shell markup or hero styling contract.
- Rework `build_site.mjs` to selectively copy locale assets in this pass.
- Touch `prototype-hero-graywhite-left.png`, `prototype-hero-graywhite-right.png`, or the active graywhite WebP files.

## Decisions

### Decision: Delete only unreferenced historical variants
This pass removes the following source files:
- `homepage-cabo-verde-inset.svg`
- `prototype-hero-dusk.webp`
- `prototype-hero-night.webp`
- `prototype-hero-sunset-right.webp`
- `prototype-hero-sunset-source.webp`
- `prototype-hero.jpg`
- `upstream-atlas-hero-v2-photo-right-fade.webp`
- `upstream-atlas-hero-v3-clean.webp`
- `upstream-atlas-hero-v4-clean.webp`
- `upstream-atlas-hero-v5-soft-left.webp`
- `upstream-atlas-hero-v6-soft-left.webp`
- `upstream-atlas-wordmark.png`
- `west-africa-intelligence-overlay.svg`

Alternative considered:
- Also remove `prototype-hero-graywhite-left.png` and `prototype-hero-graywhite-right.png`. Rejected because those files are closer to the still-active book-theme chain and the user previously asked to leave book theme alone.

### Decision: Convert existing "present but unused" assertions into "must stay absent" assertions
`scripts/test-site-render.sh` currently still checks a few of these files for size or existence even though no runtime surface references them. This change will flip that contract: the source tree and both public asset trees must keep them absent.

Alternative considered:
- Delete the files without changing tests. Rejected because `build_site.mjs` would allow silent reintroduction through later asset copies.

## Risks / Trade-offs

- [A deleted file might still be useful as historical design context] -> Accept this because the user explicitly asked to continue the asset audit and the selected set has no current runtime dependency.
- [This pass leaves copy-strategy inefficiency in place] -> Accept this because changing build-copy semantics is a separate behavioral change and deserves its own narrower pass.

## Migration Plan

1. Add failing regression checks for the unreferenced-asset absence contract.
2. Delete the unreferenced historical asset variants from `assets/images/`.
3. Rebuild the site so the variants disappear from both public asset trees.
4. Run targeted tests, site verification, and OpenSpec validation.
5. If rollback is needed, restore the deleted assets and revert the absence assertions.

## Open Questions

- None for this change.
