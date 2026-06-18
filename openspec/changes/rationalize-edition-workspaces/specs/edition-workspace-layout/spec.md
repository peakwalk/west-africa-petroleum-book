## ADDED Requirements

### Requirement: Locale-owned source inputs are organized under one edition root
The repository MUST organize each locale's mdBook config, locale catalog, landing/legal source content, Markdown content, figure assets, and figure manifest under a single `editions/<locale>/` root with a shared internal layout.

#### Scenario: English and French edition roots use the same workspace shape
- **WHEN** a contributor inspects `editions/en/` and `editions/fr/`
- **THEN** each root contains its own `book.toml`, `locale.json`, `site/`, `source/`, and `content/` directories

#### Scenario: Locale-owned content lives below the edition root
- **WHEN** a contributor inspects one edition workspace
- **THEN** the edition's `SUMMARY.md`, chapter Markdown, locale-specific legal content, published figure assets, `figure-manifest.json`, and any retained raw figure backups are all located under that edition root instead of being split across unrelated top-level directories

### Requirement: Edition configuration derives paths from the edition root
The shared edition registry MUST declare each locale using an `editionRoot` convention and MUST derive book, site, content, legal, chapter, locale-catalog, figure-root, and figure-manifest paths from that root instead of storing each derived path independently.

#### Scenario: Registry loads a locale from one root
- **WHEN** build or validation code loads an edition definition
- **THEN** the code resolves the edition's book config, site content, Markdown content, locale catalog, figure root, and figure manifest from the configured `editionRoot`

#### Scenario: Node and Python loaders resolve the same edition structure
- **WHEN** the Node site generators and Python validation scripts load the same locale from the registry
- **THEN** both runtimes resolve matching paths for that edition's book config, summary, chapters, legal content, figure root, and figure manifest

### Requirement: Legacy locale-owned source roots are retired after migration
Once the edition-root topology is active, the repository MUST NOT require locale-owned source inputs from legacy split roots such as `src-fr/`, `books/fr/`, root `book.toml`, or `config/locales/*.json`.

#### Scenario: Build inputs come only from edition workspaces
- **WHEN** the assembled site build runs after migration
- **THEN** it reads locale-owned source inputs from `editions/<locale>/` roots rather than depending on legacy locale-specific source directories outside those roots

#### Scenario: Edition workspaces can scale to an additional locale
- **WHEN** a maintainer adds another locale in the future
- **THEN** the maintainer can create one new `editions/<locale>/` workspace and register its `editionRoot` without introducing a new top-level naming convention
