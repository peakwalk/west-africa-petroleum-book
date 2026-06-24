## ADDED Requirements

### Requirement: Reader body figure images open the original asset in a new browser tab
The `/book/` reader MUST let users inspect generated body figure images by opening the original asset in a new browser tab.

#### Scenario: Clicking a body figure image opens the original asset in a new tab
- **WHEN** a reader clicks an image inside a generated `.reader-article .figure-card`
- **THEN** the reader opens that image asset in a new browser tab
- **AND** the current chapter tab remains intact

#### Scenario: Keyboard activation opens the same image in a new tab
- **WHEN** focus is on an eligible body figure image
- **AND** the user presses `Enter` or `Space`
- **THEN** the same image asset opens in a new browser tab

#### Scenario: Multi-image figures open the clicked panel only
- **WHEN** a generated figure card contains multiple images
- **AND** the reader activates one of those images
- **THEN** the new tab opens only the activated image rather than the full figure group

### Requirement: Reader image-open behavior stays scoped to body figures
The `/book/` reader MUST scope the image-open enhancement to generated body figure cards and MUST NOT attach it to non-body images.

#### Scenario: Non-body images remain unchanged
- **WHEN** an image is outside `.reader-article .figure-card`, including navigation, cover, landing-page, or decorative chrome images
- **THEN** the reader does not treat that image as openable by this enhancement
- **AND** the new-tab image-open behavior is not attached to that image
