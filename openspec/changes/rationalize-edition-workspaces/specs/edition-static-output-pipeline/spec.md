## ADDED Requirements

### Requirement: Static site generators publish directly into the assembled public tree
Landing, legal, and chapter-library generators MUST write edition-specific output directly into `public/` according to each locale's route prefix instead of generating committed static HTML under the repository root or `fr/`.

#### Scenario: English public pages are generated directly into public root
- **WHEN** the site build completes successfully
- **THEN** the English landing page, legal pages, and chapter-library page exist under `public/` without requiring committed root HTML as build inputs

#### Scenario: French public pages are generated directly into the prefixed public root
- **WHEN** the site build completes successfully
- **THEN** the French landing page, legal pages, and chapter-library page exist under `public/fr/` without requiring committed `fr/` HTML as build inputs

### Requirement: mdBook output is assembled from edition roots into route-compatible publish targets
The build pipeline MUST run each edition's mdBook build from its edition workspace and publish the reader output into `public/<routePrefix>/book`, using `public/book` for the default English edition and `public/fr/book` for the French edition.

#### Scenario: Default-locale book output keeps the current English route
- **WHEN** the English edition build runs
- **THEN** the reader output is published to `public/book/` even though the English source now lives under `editions/en/`

#### Scenario: French book output keeps the current prefixed route
- **WHEN** the French edition build runs
- **THEN** the reader output is published to `public/fr/book/` even though the French source now lives under `editions/fr/`

### Requirement: No committed generated publish pages exist outside public
After the migration completes, the repository MUST treat `public/` as the only generated publish artifact directory and MUST NOT require committed generated landing, legal, or chapter-library HTML outside `public/`.

#### Scenario: Repo root is not a source of generated static publish pages
- **WHEN** a contributor inspects the repository after the migration cleanup
- **THEN** root-level generated landing/legal/chapter HTML is absent and the build no longer depends on those files

#### Scenario: French prefixed static pages are not versioned outside public
- **WHEN** a contributor inspects the repository after the migration cleanup
- **THEN** there is no committed `fr/` static-page tree outside the assembled `public/fr/` publish output
