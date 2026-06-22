## Why

The current `AGENTS.md` tells agents to use both OpenSpec and Superpowers, but it does not draw the boundary between them precisely enough for low-risk versus high-risk work. That creates two avoidable failure modes: agents skip OpenSpec when a workflow or behavior contract changed, or they over-apply Superpowers and leave parallel durable docs that drift away from the repo's source of truth.

## What Changes

- Rewrite the repo's OpenSpec and Superpowers guidance into MECE sections that separate role boundaries, required OpenSpec cases, skippable cases, artifact rules, Superpowers usage rules, and conflict resolution.
- Add repo-local rules for OpenSpec change naming, English and Chinese companion files, and fallback locations for durable Superpowers artifacts when OpenSpec is unavailable or not required.
- Update `AGENTS.zh_CN.md` together with `AGENTS.md` so the repo keeps one bilingual workflow contract.

## Capabilities

### New Capabilities
- `agent-workflow-governance`: Defines how Africa Book agents decide when OpenSpec is mandatory, how Superpowers may assist execution, where durable workflow artifacts belong, and how conflicts are resolved.

### Modified Capabilities
- None.

## Impact

- Affected docs: `AGENTS.md`, `AGENTS.zh_CN.md`
- New OpenSpec change artifacts under `openspec/changes/chg-20260622-140453-clarify-agent-workflow/`
- Fallback documentation roots referenced by policy: `docs/superpowers/specs/`, `docs/superpowers/plans/`
- No book content, build output, or figure assets change directly
