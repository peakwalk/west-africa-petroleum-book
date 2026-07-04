## ADDED Requirements

### Requirement: Preview rebuilds after render-affecting source changes
`npm run preview` MUST continue running after startup and MUST rebuild the assembled site when render-affecting source files change.

#### Scenario: Styles or content change during preview
- **WHEN** the user edits a watched stylesheet, template, chapter, image, or preview build script while `npm run preview` is running
- **THEN** the preview workflow reruns the assembled-site build
- **AND** the refreshed output is written back into the existing `public/` tree

#### Scenario: A second change arrives during an active rebuild
- **WHEN** another watched file changes while the preview workflow is already rebuilding
- **THEN** the workflow does not start a concurrent second rebuild
- **AND** it schedules one follow-up rebuild after the current rebuild completes

### Requirement: Preview pages reload only after successful rebuilds
Preview pages served by the preview server MUST reload automatically after a successful rebuild and MUST avoid forcing a reload for failed rebuilds.

#### Scenario: Successful rebuild advances the preview session
- **WHEN** a watched change triggers a successful preview rebuild
- **THEN** open preview pages receive a changed reload token
- **AND** the browser reloads the current page automatically

#### Scenario: Failed rebuild keeps the previous page stable
- **WHEN** a watched change triggers a rebuild failure
- **THEN** the preview workflow keeps serving the last successful `public/` output
- **AND** open preview pages do not auto-reload into a broken state

### Requirement: Preview-only reload code does not alter published files on disk
The browser auto-reload mechanism MUST remain a preview-only serving concern and MUST NOT rewrite the built HTML files stored under `public/`.

#### Scenario: Reload helper is injected only while serving preview HTML
- **WHEN** the preview server returns an HTML page while preview auto reload is enabled
- **THEN** the response includes the preview reload helper
- **AND** the corresponding HTML file on disk remains unchanged
