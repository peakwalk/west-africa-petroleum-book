## ADDED Requirements

### Requirement: Online figure number controls the published asset name
The system SHALL use the online figure number as the English published asset identifier when UA-19 source artwork uses a development-era filename. The required mappings are Jira `figure-008.png` to online Figure 9 and `figure-009.{png,webp}`, Jira `figure-040.png` to online Figure 41 and `figure-041.{png,webp}`, and Jira `figure-068.png` to online Figure 69 and `figure-069.{png,webp}`.

#### Scenario: Low-numbered Jira artwork is prepared for publication
- **WHEN** an implementer receives UA-19's `figure-008.png`, `figure-040.png`, and `figure-068.png` attachments
- **THEN** the revised English assets are saved and published as `figure-009`, `figure-041`, and `figure-069` respectively

#### Scenario: Adjacent figures are protected
- **WHEN** the three revised assets are published
- **THEN** the assets for online Figures 8, 40, and 68 are not replaced by the Jira attachments

### Requirement: Figure 9 uses reviewed petroleum-product terminology
The published online Figure 9 SHALL replace “Heavy Gasoline (Intermediate)” with “Heavy Naphtha” and “Kerosene” with “Jet Fuel (Kerosene)”. It SHALL preserve the existing product order, visual style, layout, and caption.

#### Scenario: Reader views online Figure 9
- **WHEN** the English Figure 9 is rendered in the book
- **THEN** it displays the two reviewed terms in their existing product positions without changing the figure caption or product order

### Requirement: Figure 41 represents the reviewed modelling flow
The published online Figure 41 SHALL show Reservoir Models and Reservoir Understanding as outputs of Integration and Modelling and as inputs to Evaluation and Recovery Options. Every displayed workflow arrow SHALL have a valid start and end point, and the redundant right-side arrow from Box 2 SHALL be absent.

#### Scenario: Reader follows the Figure 41 workflow
- **WHEN** the English Figure 41 is rendered in the book
- **THEN** the modelling outputs flow into Evaluation and Recovery Options and no dangling arrow is visible

### Requirement: Figure 69 represents the reviewed PSC revenue flow
The published online Figure 69 SHALL show Gross Revenue, Recoverable Costs (Cost Oil / Cost Gas), Profit Oil / Profit Gas, Government Share, and Contractor Share in that logical order. Recoverable Costs SHALL list Exploration, Development, Operating, and Abandonment / Decommissioning Costs. The figure SHALL rename “Uses of Government Take” to “Components of Government Take” and describe Profit Oil / Profit Gas as “Remaining revenue after recovery of allowable costs.”

#### Scenario: Reader follows the Figure 69 revenue allocation
- **WHEN** the English Figure 69 is rendered in the book
- **THEN** Recoverable Costs are distinct from Profit Oil / Profit Gas and Government Share and Contractor Share derive from Profit Oil / Profit Gas

### Requirement: Revised figures remain publishable and traceable
The implementation SHALL retain the revised PNG source assets, generate non-empty English WebP publication assets, rebuild the English figure manifest, and preserve existing chapter references and captions. It SHALL not hand-edit `public/` or alter French-edition assets.

#### Scenario: English site is rebuilt after the figure update
- **WHEN** the project builds the English site and runs figure validation
- **THEN** the manifest and figure checks succeed and the generated pages reference the updated 009, 041, and 069 WebP assets

### Requirement: Paired visual review evidence is captured
Before replacing a target figure, the implementation SHALL capture a baseline screenshot of each affected English figure in the built reader. After implementation and site rebuild, it SHALL capture matching updated screenshots with the same browser engine, route, viewport, full-page setting, and figure-specific name. The baseline and updated artifacts SHALL be retained under `output/playwright/ua-19-technical-figure-corrections/` and delivered together for human review.

#### Scenario: Reviewer compares the completed change
- **WHEN** implementation validation has completed
- **THEN** the reviewer receives paired baseline and updated screenshots for Figures 9, 41, and 69 that can be compared under identical capture conditions
