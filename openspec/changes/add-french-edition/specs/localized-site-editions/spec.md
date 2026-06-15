## ADDED Requirements

### Requirement: Edition-specific public routes
The site MUST publish the English edition on the current root routes and MUST publish a French edition under `/fr/`. The French edition MUST include localized home, legal, chapter-library, and book routes without overwriting the English outputs.

#### Scenario: Dual public roots are generated
- **WHEN** the site build completes successfully
- **THEN** the output contains `public/index.html`, `public/book/index.html`, `public/fr/index.html`, and `public/fr/book/index.html`

#### Scenario: French build does not replace English output
- **WHEN** the French edition is generated after the English edition
- **THEN** the existing English root files remain present and their route prefixes remain unchanged

### Requirement: Browser-language edition auto-selection on neutral entry routes
Edition-neutral entry routes MUST default to English for readers without a French browser-language preference, and MUST automatically redirect to the equivalent French entry route when the browser prefers French. This negotiation MUST be limited to edition-neutral entry routes and MUST NOT force-redirect explicit edition URLs.

#### Scenario: Neutral landing entry defaults to English
- **WHEN** a reader opens the neutral landing entry route and the browser language preference is not French
- **THEN** the English landing page remains visible

#### Scenario: Neutral landing entry redirects French browsers
- **WHEN** a reader opens the neutral landing entry route and the browser language preference indicates French
- **THEN** the page redirects to the French landing route before the reader starts navigating the site

#### Scenario: Neutral book entry redirects French browsers
- **WHEN** a reader opens the neutral book entry route and the browser language preference indicates French
- **THEN** the page redirects to the French book entry route instead of staying on the English book entry route

#### Scenario: Explicit edition routes are respected
- **WHEN** a reader directly opens `/fr/...` or an explicit English route chosen from the language switch
- **THEN** the site does not override that explicit route selection just because the browser prefers another language

### Requirement: Localized public copy and navigation labels
Each edition MUST render its own public-facing labels for header, footer, legal navigation, chapter-library UI, and book-reader shell. Shared layout structure MAY remain the same, but user-visible copy MUST match the edition locale.

#### Scenario: Landing shell labels follow the edition locale
- **WHEN** a reader opens the English and French landing pages
- **THEN** the navigation labels, CTA labels, footer headings, and legal headings are rendered in English on the root edition and in French on the `/fr/` edition

#### Scenario: Reader shell labels follow the edition locale
- **WHEN** a reader opens `/book/` and `/fr/book/`
- **THEN** toolbar labels, search placeholder text, outline headings, and chapter-pagination labels are localized per edition

### Requirement: Cross-edition language switching
Every public page family that exists in both editions MUST expose a language switch so a reader can move between the English and French equivalents. Equivalent pages MUST preserve the same content target whenever the slug exists in both editions.

#### Scenario: Landing header exposes the language switch
- **WHEN** a reader opens the English or French landing page
- **THEN** the page header renders a visible language-switch control that links to the equivalent landing page in the other edition

#### Scenario: Book header exposes the language switch
- **WHEN** a reader opens the English or French book reader
- **THEN** the sticky book header renders a visible language-switch control that links to the equivalent book page in the other edition

#### Scenario: Book header language switch keeps the chapter target
- **WHEN** a reader is on a localized book chapter whose slug exists in both editions and activates the language switch from the book header
- **THEN** the destination opens the same chapter slug under the other edition prefix

#### Scenario: Landing and legal pages switch to their edition peers
- **WHEN** a reader activates the language switch from a landing page, legal page, or chapter-library page
- **THEN** the destination opens the corresponding page in the other edition instead of a generic homepage fallback
