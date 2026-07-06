## ADDED Requirements

### Requirement: Homepage search surface MUST match the approved centered search reference
The generated homepage SHALL render its search section as a centered search-entry surface with one visible title and one integrated pill-shaped search field, rather than a duplicated visible heading stack plus a detached submit button.

#### Scenario: Desktop layout follows the approved search composition
- **WHEN** the homepage renders on desktop widths
- **THEN** the search section shows one centered visible title above the form
- **THEN** the form renders as a wide rounded search field with an embedded leading search control or icon, not a separate submit button positioned to the right
- **THEN** the localized placeholder text remains visible inside the field

#### Scenario: Search routing remains unchanged
- **WHEN** a user submits the homepage search form
- **THEN** the form sends the existing `search` query parameter to the same book route currently used by the homepage
- **THEN** the search-scope chips below the field continue linking to their existing search destinations
- **THEN** each search-scope chip renders a leading icon and spacing treatment that matches the approved reference without changing its destination

#### Scenario: Narrow viewports keep the search surface usable
- **WHEN** the homepage renders on tablet or mobile widths
- **THEN** the integrated icon and input remain visible without clipping
- **THEN** the form fits within the shared landing content width and keeps localized text readable
