## Overview

The deployed site already has a single canonical output root: `public/`. The cleanup should align standalone landing-generation entrypoints with that contract and remove the older root-level tracked HTML files that no build or deployment workflow consumes.

## Decisions

1. Delete the tracked root-level landing outputs instead of trying to keep them in sync.
2. Keep `--output-root` overrides intact for tests and build orchestration.
3. Change the default output root in the three standalone generators to `public/`.
4. Make the package script aliases explicit so the default destination is visible from `package.json`.
5. Add regression assertions that fail if root landing outputs reappear or if landing pages start referencing extra PNG assets again.

## Non-Goals

- Do not change the mdBook reader output under `book/` or `public/book/`.
- Do not change deployed landing markup or locale routing.
- Do not alter book-theme favicon behavior in this cleanup.

## Verification

- Run `python3 -m unittest tests.test_public_editions`.
- Run `npm run build:site`.
- Run `npm run test:site`.
