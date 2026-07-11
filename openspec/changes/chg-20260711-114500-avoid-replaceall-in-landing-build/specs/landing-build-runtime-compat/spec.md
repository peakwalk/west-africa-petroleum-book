## MODIFIED Requirements

### Requirement: Landing build helpers MUST stay compatible with preview runtimes

Helpers used by landing-generation entrypoints MUST avoid JavaScript string APIs that break the supported local preview runtimes when an older engine executes `npm run preview`.

#### Scenario: outline icon escaping does not depend on replaceAll

- **WHEN** the landing build renders homepage outline icons
- **THEN** `scripts/shared/homepage-outline-icons.mjs` does not call `replaceAll`
- **AND** landing generation still HTML-escapes class names and icon names before inlining SVG markup
