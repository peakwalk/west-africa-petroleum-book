## Why

The current repository `AGENTS.md` defines workflow, validation, and localization rules, but it does not define any line-count guidance for handwritten source files. That leaves agents without a repo-local constraint when a stylesheet, template, or generator file keeps growing. The result is predictable: reviewability degrades, localized changes become harder to isolate, and large files such as landing-page stylesheets accumulate unrelated concerns.

The `oae-mono` reference repository already solves this with explicit file-size guidance. Africa Book needs the same kind of rule, but adapted to its own surfaces: handwritten source files in general, plus landing-page stylesheets, templates, and page-generation scripts in particular.

## What Changes

- Add a repo-local file-size guidance section to `AGENTS.md` for handwritten source files.
- Add the aligned Simplified Chinese rule set to `AGENTS.zh_CN.md`.
- Define the policy in OpenSpec under the existing `agent-workflow-governance` capability so future workflow edits have a durable contract.

## Capabilities

### Modified Capabilities
- `agent-workflow-governance`: The repository workflow contract now includes reviewability-focused line-count guidance for handwritten source files and expectations for editing already-oversized files.

## Impact

- Affected docs: `AGENTS.md`, `AGENTS.zh_CN.md`
- New OpenSpec change artifacts under `openspec/changes/chg-20260703-142449-add-code-size-guidance/`
- No book content, generated site output, figure assets, or landing-page behavior changes directly
