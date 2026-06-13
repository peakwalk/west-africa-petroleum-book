## ADDED Requirements

### Requirement: Query-driven local filtering
The book search box MUST filter local mdBook index records in real time as the query changes. Matching MUST be case-insensitive and MUST consider the indexed `title`, `body`, and `breadcrumbs` fields. When the trimmed query is empty, the result set MUST be empty instead of showing all indexed items.

#### Scenario: Query matches across indexed fields
- **WHEN** a reader types a non-empty query that exists in a result title, body excerpt, or breadcrumbs label
- **THEN** the search box returns only records whose indexed text contains that query, regardless of case

#### Scenario: Empty query clears results
- **WHEN** a reader removes all text from the search input
- **THEN** the search box stores an empty result set and does not show all indexed items

### Requirement: Focused dropdown visibility and dismissal
The book search box MUST show its results panel only while the input is focused and the trimmed query is non-empty. The panel MUST close when the user presses `Escape` or clicks outside both the search input shell and the results panel. Dismissal MUST be implemented from a `mousedown` listener rather than relying on input `blur`.

#### Scenario: Focus plus query opens the panel
- **WHEN** the search input is focused and the trimmed query contains at least one character
- **THEN** the results panel is displayed directly beneath the input as a dropdown

#### Scenario: Outside click closes the panel
- **WHEN** the user presses the mouse button on a target outside the search input shell and outside the results panel
- **THEN** the search box marks the input as not focused and closes the dropdown without waiting for an `onBlur` callback

### Requirement: Clear action and focus-preserving input state
The book search box MUST render a clear control inside the input whenever the query is non-empty. Activating the clear control MUST empty the query and return focus to the search input. The search UI MUST widen slightly while focused through a JavaScript-controlled state class rather than relying on CSS `:focus` alone.

#### Scenario: Clear control resets the query without blur
- **WHEN** the query is non-empty and the user activates the clear control
- **THEN** the control prevents the `mousedown` blur, clears the query value, and focuses the input again

#### Scenario: Focus state changes input width
- **WHEN** the search input enters or leaves the focused state
- **THEN** the search shell toggles a stateful class that controls the expanded input width

### Requirement: Result rendering and highlighting
The book search box MUST render each result with a type icon, highlighted title text, a visible breadcrumbs label, and a highlighted excerpt. Highlighting MUST split text by a case-insensitive query regex and wrap each match in a `<mark>` element. The results panel MUST also render a result-count header and an empty state with an icon and message when no results match.

#### Scenario: Matching results show highlighted fields
- **WHEN** the query matches one or more indexed records
- **THEN** each rendered result includes a type marker, title with `<mark>` around matches, breadcrumbs label, and excerpt with `<mark>` around matches

#### Scenario: No matches show an empty state
- **WHEN** the query is non-empty and no indexed records match
- **THEN** the dropdown stays open and renders a result-count header plus an empty-state row with an icon and explanatory message

### Requirement: Keyboard navigation of visible results
The book search box MUST support keyboard navigation while the dropdown is visible. `ArrowDown` and `ArrowUp` MUST move an active result index, `Enter` MUST open the active result, and `Escape` MUST close the panel and blur the input.

#### Scenario: Arrow keys move the active result
- **WHEN** the dropdown is visible and the user presses `ArrowDown` or `ArrowUp`
- **THEN** the search box updates which result is active without submitting the form

#### Scenario: Enter opens the active result
- **WHEN** the dropdown is visible, a result is active, and the user presses `Enter`
- **THEN** the reader navigates to that result target
