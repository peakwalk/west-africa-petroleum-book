## ADDED Requirements

### Requirement: Homepage shell MUST orient first-time visitors around the approved primary actions
The public homepage SHALL provide a shared shell that immediately explains the product and exposes the approved primary actions for `Countries`, `Chapters`, `Search`, and `Contact`. Obsolete top-level `Resources` and `About` entries MUST NOT remain in the primary homepage navigation.

#### Scenario: Homepage navigation exposes the approved primary actions
- **WHEN** a user opens the public homepage
- **THEN** the top navigation includes direct actions for `Countries`, `Chapters`, `Search`, and `Contact`
- **THEN** `Countries`, `Chapters`, and `Search` resolve to the matching homepage sections for country discovery, topic discovery, and book search
- **THEN** the primary navigation does not include legacy `Resources` or `About` items

#### Scenario: Hero orients the user toward the current edition
- **WHEN** a user lands on the English homepage
- **THEN** the hero explains the independent West Africa petroleum-reference positioning
- **THEN** it includes a clear current-edition entry point into the existing book surface

### Requirement: Homepage MUST provide country-led discovery for all covered West African countries
The homepage SHALL expose `Coverage Across West Africa` as the dominant exploration surface. It SHALL list the 16 covered countries as uniform cards with consistent sizing, status labeling, ministry metadata, national oil company metadata, scale metrics, and a CTA into the appropriate chapter-3 country subsection.

#### Scenario: Country cards provide complete country entry points
- **WHEN** the English homepage renders the country-discovery section
- **THEN** it includes one card for each of the 16 covered West African countries
- **THEN** each card exposes status, ministry/NOC information, scale metrics, and a country CTA

#### Scenario: Country cards deep-link into the book
- **WHEN** a user activates a country CTA such as Nigeria
- **THEN** the destination resolves to the appropriate chapter-3 country anchor inside the existing book output

### Requirement: Homepage MUST provide a geographic map as a secondary country-navigation aid
The homepage SHALL include a clickable West Africa political map that provides geographic navigation to the same country destinations as the country cards. The map MUST remain supplementary to the card grid and MUST NOT introduce a second, conflicting country-routing model.

#### Scenario: Map routes to the same destination as the country card
- **WHEN** a user selects a country from the West Africa map
- **THEN** the resulting destination matches the destination used by that country's card CTA

#### Scenario: Map remains supplemental to the card grid
- **WHEN** the homepage renders on desktop or mobile
- **THEN** the country card grid still provides a complete country-discovery path even if the user does not interact with the map

### Requirement: Homepage MUST provide topic discovery that does not overlap with country discovery
The homepage SHALL replace `Explore the Reference Library` with `Browse by Topic` and use that section for curated thematic entry points into the existing book chapters. Topic discovery MUST remain distinct from both country discovery and search.

#### Scenario: Browse by Topic points to approved chapter destinations
- **WHEN** the homepage renders the topic-discovery section
- **THEN** the section label is `Browse by Topic`
- **THEN** each topic card links to an approved canonical chapter destination in the existing book

#### Scenario: Topic browsing remains distinct from country browsing
- **WHEN** a user scans the homepage
- **THEN** country entry points appear in the country-discovery section
- **THEN** thematic chapter entry points appear in `Browse by Topic`
- **THEN** the two modules do not duplicate the same primary purpose

### Requirement: Homepage MUST provide a book-only search entry
The homepage SHALL include a `Search Upstream Atlas` section that routes users into the existing online-book search surface. The section MUST clearly communicate that it searches the book only and MUST NOT imply a separate site-wide search backend in this phase.

#### Scenario: Search section routes into the existing book search experience
- **WHEN** a user uses the homepage search entry
- **THEN** the flow resolves into the existing mdBook search surface for the online book
- **THEN** the section copy indicates that the search scope is the book content

### Requirement: Homepage MUST communicate freshness, edition state, and contact paths
The homepage SHALL replace the low-signal authors module with `Latest Updates`, keep a `Current Edition` module, simplify `Future Development`, and expand footer coverage/contact messaging. Shared shell actions for search and contact SHALL remain locale-safe in both English and French builds.

#### Scenario: Latest Updates replaces the authors module
- **WHEN** the homepage renders the trust-and-freshness section
- **THEN** it presents `Latest Updates` rather than an authors block
- **THEN** it communicates recent release or data-update signals

#### Scenario: Contact action is directly available and locale-safe
- **WHEN** a user activates the homepage contact action from either English or French
- **THEN** the action opens the approved Upstream Atlas contact destination with the maintained recipient and subject behavior
- **THEN** the shared shell does not send the user to a broken or locale-inappropriate target
