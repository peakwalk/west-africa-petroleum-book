## ADDED Requirements

### Requirement: Landing stylesheet sources MUST remain modular while preserving the public entrypoint
The repository MUST keep `assets/css/landing.css` as the public landing-page stylesheet entrypoint used by generated HTML, but the handwritten landing-page source rules MUST be organized into smaller coherent modules instead of one ever-growing stylesheet. The modularization MUST preserve current asset references and rendered homepage behavior.

#### Scenario: Generated HTML keeps the same landing stylesheet path
- **WHEN** the site generator renders the English or French homepage
- **THEN** the HTML still links to `assets/css/landing.css` as the public landing stylesheet entrypoint

#### Scenario: Modular sources preserve homepage rendering behavior
- **WHEN** the landing stylesheet source is split into smaller modules
- **THEN** the resulting homepage rendering keeps the same intended visual behavior and asset resolution as before the split

### Requirement: Landing stylesheet validation MUST evaluate expanded imported CSS
If `assets/css/landing.css` becomes a thin import manifest, landing stylesheet validation MUST expand local imports before checking for expected selectors and declarations so assertions remain semantically equivalent to the pre-split validation.

#### Scenario: Assertions still see hero and header rules after the split
- **WHEN** site-render validation checks landing CSS after modularization
- **THEN** the validation expands imported landing CSS modules before checking for expected header, hero, navigation, and responsive declarations
