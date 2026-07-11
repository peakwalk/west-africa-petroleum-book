## ADDED Requirements

### Requirement: English country cards expose published chapter labels
The generated English homepage SHALL render exactly 16 country-card analysis links. Each link SHALL display the published English `Chapter 3.X →` label for its country:

| Country | Label |
| --- | --- |
| Nigeria | `Chapter 3.1 →` |
| Ghana | `Chapter 3.2 →` |
| Côte d'Ivoire | `Chapter 3.3 →` |
| Senegal | `Chapter 3.4 →` |
| Mauritania | `Chapter 3.5 →` |
| Niger | `Chapter 3.6 →` |
| Benin | `Chapter 3.7 →` |
| Liberia | `Chapter 3.8 →` |
| Sierra Leone | `Chapter 3.9 →` |
| Guinea | `Chapter 3.10 →` |
| Guinea-Bissau | `Chapter 3.11 →` |
| The Gambia | `Chapter 3.12 →` |
| Togo | `Chapter 3.13 →` |
| Burkina Faso | `Chapter 3.14 →` |
| Mali | `Chapter 3.15 →` |
| Cabo Verde | `Chapter 3.16 →` |

#### Scenario: English homepage renders all chapter labels
- **WHEN** the English homepage is generated
- **THEN** each of the 16 country cards has the required label for its country
- **AND** no country-card analysis link displays `Country Analysis →`

### Requirement: Country-card destinations remain unchanged
Each generated English country-card analysis link SHALL retain its existing chapter URL and country fragment.

#### Scenario: Country-card labels retain their destinations
- **WHEN** the English homepage is generated with chapter labels
- **THEN** every country-card analysis link has the same `href` it had before this change
- **AND** each `href` targets the English Chapter 3 country-analysis page and its country-specific fragment

### Requirement: Other editions and presentation remain stable
The change SHALL not alter the French compatibility homepage's country-navigation behaviour, nor change the English card link's existing markup classes or presentation rules.

#### Scenario: Generated edition pages preserve their existing presentation contract
- **WHEN** the English and French homepages are generated after the change
- **THEN** the English card analysis links retain the `country-analysis-link` class and existing destination format
- **AND** the French compatibility homepage retains its existing country-navigation output
