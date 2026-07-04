## Context

Africa Book is not a React monorepo, but it still has handwritten files that can grow into review hazards: `assets/css/landing.css`, landing-page generator scripts, shared content modules, templates, and repo-local workflow docs. The repo already has strong rules for localization pairing, OpenSpec usage, figure workflow, and validation. What is missing is a small, explicit rule that keeps handwritten source files reviewable and prevents large files from growing indefinitely.

The `oae-mono` reference repo already provides a useful pattern:
- use guidance thresholds instead of a hard compiler-style failure,
- distinguish normal source files from especially growth-prone UI containers,
- require justification for very large new files,
- and avoid growing files that are already oversized.

That pattern transfers well to Africa Book if we adapt the second category from React route pages to this repo's risky surfaces: landing-page stylesheets, site templates, and page-generation scripts.

## Goals / Non-Goals

**Goals:**
- Add a reviewability-oriented line-count rule for handwritten source files.
- Make the rule directly useful for this repo's high-growth surfaces: stylesheets, templates, and generator scripts.
- Keep the rule practical by treating it as guidance plus an escalation threshold, not as an automatic hard stop for every edge case.
- Preserve exemptions for generated files and similar artifacts that should not be hand-optimized for line count.

**Non-Goals:**
- Refactor existing oversized files in this change.
- Introduce new tooling that automatically enforces file size.
- Define separate limits for every file extension in the repo.

## Decisions

### 1. Use guidance thresholds instead of a hard ban

The repo rule should guide agent behavior during planning and editing, not behave like a build breaker. That means the language should say files "should normally" stay under the threshold, while still requiring explicit justification for extreme cases.

### 2. Keep one general threshold and one repo-specific stricter threshold

The policy will use:
- a general threshold of 600 lines for new handwritten source files,
- a stricter 500-line threshold for landing-page stylesheets, site templates, and page-generation scripts,
- and an escalation threshold of 800 lines for any new handwritten source file.

This keeps the rule simple and directly addresses the files most likely to become hard to review in Africa Book.

### 3. Oversized existing files must not keep growing casually

The most important practical rule is not only about new files. When a file already exceeds the threshold, agents should avoid increasing its size. For non-trivial edits, they should extract at least one coherent partial, helper, content module, or script split unless that extraction would create unrelated churn.

### 4. Keep exemptions explicit

Generated files, lockfiles, snapshots, fixture data, vendored references, and migration-style artifacts should stay exempt. That keeps the rule focused on handwritten maintainability rather than mechanically penalizing generated output.

## Risks / Trade-offs

- [A strict rule could slow small urgent fixes] -> Use "normally" guidance plus an 800-line exception threshold instead of an unconditional ban.
- [The repo could still accumulate legacy oversized files] -> Require agents not to grow them casually and to extract at least one coherent unit for non-trivial edits.
- [Different file types have different density] -> Keep only two thresholds so the rule stays memorable and enforceable in practice.

## Migration Plan

- Update `AGENTS.md` and `AGENTS.zh_CN.md` in the same change.
- Reference the new rule through the existing workflow-governance capability.
- Do not attempt cleanup refactors of existing oversized files as part of this policy-only update.

## Open Questions

- None.
