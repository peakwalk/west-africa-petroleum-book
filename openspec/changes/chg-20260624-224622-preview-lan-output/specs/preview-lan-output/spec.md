## ADDED Requirements

### Requirement: Preview startup announces a LAN-reachable URL by default
`npm run preview` MUST announce a LAN-reachable URL when using its default bind configuration.

#### Scenario: Default preview output shows a LAN-friendly address
- **WHEN** the user runs `npm run preview` without overriding the host
- **THEN** the preview server binds on `0.0.0.0`
- **AND** the startup output shows a LAN-reachable display address instead of `127.0.0.1` or `0.0.0.0`

#### Scenario: Preview server banner matches the wrapper output
- **WHEN** the preview server starts
- **THEN** the Python server banner shows the same display host and port as the shell wrapper output

### Requirement: Preview startup remains override-friendly
`npm run preview` MUST preserve explicit override paths for unusual local networking environments.

#### Scenario: Explicit display-host override is honored
- **WHEN** the user sets an explicit preview display-host override
- **THEN** the startup output uses that override value
- **AND** the Python server banner uses the same override value
