## Why

The current homepage white-surface sections use several near-matching blues for headings, body copy, metadata, and interactive text. That drift makes the landing page feel like adjacent modules belong to different systems even when the layout is already aligned to the approved reference.

The user has now asked for a focused review and follow-up fix specifically around text-color consistency. We need a narrow homepage change that rationalizes those text roles without reopening layout, copy, routing, or broader visual direction decisions that were already approved in recent homepage work.

## What Changes

- Introduce a tighter homepage text-color role set for white-surface landing sections so headings, supporting copy, metadata, and interactive text no longer compete with one another.
- Replace hard-coded near-duplicate blue values in homepage CSS with shared tokens or shared role assignments wherever those values represent the same semantic text role.
- Reduce overuse of emphasis blue in supporting modules such as summary cards, topic cards, search chips, and inline explanatory copy so actionable text remains visually distinct from descriptive text.
- Preserve the current homepage layout, card composition, iconography, copy, and destinations while adjusting only text-color hierarchy and the smallest related hover-state color assignments.

## Capabilities

### New Capabilities
- `homepage-text-color-consistency`: The homepage white-surface content areas render a consistent text-color hierarchy where headings, descriptive copy, metadata, and interactive text follow shared visual roles instead of module-specific near-duplicate blues.

### Modified Capabilities
- None.

## Impact

- Affected landing tokens and shared colors: `assets/css/landing.base.css`
- Affected homepage section styles: `assets/css/landing.header.css`, `assets/css/landing.discovery.css`, `assets/css/landing.homepage-v2.css`, `assets/css/landing.modules.css`, `assets/css/landing.components.css`
- Possibly affected responsive polish if any text role needs mobile/tablet follow-through: `assets/css/landing.responsive-tablet.css`, `assets/css/landing.responsive-mobile.css`
- Affected verification: focused site-render or CSS assertions that cover homepage styling
- No intended routing, copy, asset, or structural HTML changes
