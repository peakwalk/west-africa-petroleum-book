## ADDED Requirements

### Requirement: Agents MUST classify OpenSpec need before broad implementation
Before broad implementation, agents MUST decide whether the change requires OpenSpec by evaluating repo-specific surfaces. For Africa Book, OpenSpec MUST be created or updated for user-visible book or site behavior changes, figure rendering or metadata behavior, DOCX parity behavior, landing-page generation, build or validation workflow changes, workflow policy changes, cross-edition or multi-chapter or multi-script changes, architectural refactors, and any change whose acceptance, rollback, or regression boundaries would otherwise be ambiguous.

#### Scenario: Workflow policy change requires an OpenSpec change
- **WHEN** an agent updates repository workflow policy such as `AGENTS.md`
- **THEN** the agent creates or updates an OpenSpec change before broad implementation of that policy change

#### Scenario: Narrow copy edit can skip OpenSpec
- **WHEN** an agent fixes a typo or performs a narrow copy edit that does not change workflow rules, validation expectations, or operational behavior
- **THEN** the agent may skip OpenSpec for that edit

#### Scenario: Skipped change grows beyond narrow scope
- **WHEN** a change that originally skipped OpenSpec expands into behavior, workflow, or validation policy changes
- **THEN** the agent stops and creates or updates an OpenSpec change before continuing

### Requirement: The active OpenSpec change MUST remain the canonical durable source of truth
When `openspec/changes/<change-name>/` exists for a change, durable design, task, acceptance, validation, and review decisions MUST live there. Agents MUST keep English and Simplified Chinese companion files aligned for proposal, design, tasks, and spec artifacts in the same change.

#### Scenario: Durable planning notes stay in the active change
- **WHEN** an agent produces durable planning or review notes for a change that already has `openspec/changes/<change-name>/`
- **THEN** the agent stores those durable notes in that change directory instead of creating a parallel durable source of truth elsewhere

#### Scenario: Chinese companion files are updated with English OpenSpec artifacts
- **WHEN** an agent creates or updates `proposal.md`, `design.md`, `tasks.md`, or `specs/<capability>/spec.md`
- **THEN** the agent also creates or updates the matching `.zh_CN.md` companion file in the same change

### Requirement: Superpowers MUST remain selective and subordinate to repo rules
Agents MUST use Superpowers only when it materially improves clarification, planning, testing discipline, incremental execution, or review. Agents MUST NOT assume the full upstream Superpowers workflow is enabled, and user instructions, repo-local skills, and repository workflow rules MUST override upstream Superpowers habits such as TDD-only execution, git worktrees, or branch-cleanup flows.

#### Scenario: Upstream TDD-only guidance does not override repo-local rules
- **WHEN** an upstream Superpowers skill suggests a TDD-only flow for a task that does not need it in this repository
- **THEN** the agent follows the repository's local workflow rules and user instructions instead of forcing TDD-only execution

#### Scenario: Repo-local figure workflow still takes priority
- **WHEN** work touches chapters, DOCX parity, figures, mdBook output, or generated site assets
- **THEN** the agent still follows `.agents/skills/mdbook-docx-figure-workflow/SKILL.md` as the required repo-local workflow reference

### Requirement: Durable Superpowers artifacts MUST use approved locations
If OpenSpec is unavailable or not required, durable Superpowers artifacts MUST be stored under `docs/superpowers/specs/` or `docs/superpowers/plans/` with sortable timestamped filenames. When an active OpenSpec change exists, agents MUST NOT create parallel durable docs for the same change outside the change directory unless they are clearly marked as supporting evidence that points back to the canonical OpenSpec path.

#### Scenario: No active OpenSpec change uses fallback Superpowers directories
- **WHEN** an agent needs to save a durable Superpowers design or plan and no active OpenSpec change exists because OpenSpec is unavailable or not required
- **THEN** the agent stores it under `docs/superpowers/specs/` or `docs/superpowers/plans/` with a sortable timestamp prefix

#### Scenario: Active OpenSpec change forbids parallel durable plan docs
- **WHEN** an active OpenSpec change already exists for the work
- **THEN** the agent does not create a second durable design or plan document under `docs/superpowers/**` for that same change unless it is clearly labeled as supporting evidence and points back to the canonical change path

### Requirement: Completion claims MUST include implementation and repo-relevant verification
Agents MUST NOT claim completion from an OpenSpec update alone or from Superpowers planning alone. For OpenSpec-backed changes, completion MUST include the implemented edits, the narrowest relevant repository verification, and OpenSpec validation when available in the repo.

#### Scenario: OpenSpec-only update is not enough to claim completion
- **WHEN** an agent has updated OpenSpec artifacts but has not implemented the requested change or run the relevant verification
- **THEN** the agent does not claim that the work is complete
