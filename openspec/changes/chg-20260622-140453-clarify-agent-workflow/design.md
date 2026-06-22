## Context

The current `AGENTS.md` compresses OpenSpec and Superpowers into a short bullet list. That is enough to signal intent, but not enough to answer four recurring questions reliably: whether a change needs OpenSpec, whether low-risk documentation or validation edits can skip it, where durable planning notes should live, and whether upstream Superpowers habits can override repo-specific workflow constraints. The `oae-mono` reference repo already resolves those ambiguities with clearer boundaries. Africa Book needs the same precision, but adapted to its book, site, figure, localization, and validation workflow instead of copied from an application monorepo.

## Goals / Non-Goals

**Goals:**
- Give agents a first-principles decision path: classify the change, decide whether OpenSpec is required, decide whether Superpowers helps, and decide where durable artifacts live.
- Keep the rules MECE by splitting them into required OpenSpec cases, skippable cases, artifact rules, Superpowers usage rules, and conflict and completion rules.
- Preserve existing repo-specific priorities such as localization pairing, figure workflow rules, and narrowest-useful validation.

**Non-Goals:**
- Change book or site behavior, build scripts, or figure pipelines.
- Require the full upstream Superpowers workflow for every task.
- Retroactively rename or migrate historical OpenSpec change directories.

## Decisions

### 1. Separate durable change intent from execution technique

OpenSpec owns durable change intent: scope, requirements, validation, and rollback. Superpowers only assists execution technique: clarification, planning, testing discipline, and review. This removes ambiguity about which system wins when both are relevant.

Alternative considered:
- Keep a blended bullet list with no explicit ownership. Rejected because it forces agents to infer policy boundaries case by case.

### 2. Use repo-shaped OpenSpec requirement categories

The required versus skippable rules should name Africa Book surfaces directly: book or site behavior, figure pipeline, DOCX parity, landing pages, build and validation workflows, cross-edition changes, generated outputs, and workflow policy. That is clearer here than generic software architecture labels alone.

Alternative considered:
- Copy the `oae-mono` rule list verbatim. Rejected because much of that taxonomy is app or backend specific and would add noise in this repository.

### 3. Make the active OpenSpec change the only durable source of truth for the same change

When an active change exists, plans, review notes, acceptance decisions, and spec deltas must live with it. Fallback `docs/superpowers/**` paths are allowed only when OpenSpec is unavailable or not required. This prevents split-brain planning.

Alternative considered:
- Allow both OpenSpec and `docs/superpowers/**` to hold parallel durable plans for the same work. Rejected because it creates drift during iterative edits.

### 4. Keep bilingual OpenSpec artifacts mandatory

This repo already requires Simplified Chinese companions for project workflow docs. The same rule should be explicit for OpenSpec artifacts so workflow governance does not become the exception to the repo's localization contract.

Alternative considered:
- Keep Chinese companions optional for OpenSpec. Rejected because it would create a hidden exception inside the repo's own documentation rules.

### 5. Treat upstream Superpowers skills as advisory under repo control

Local AGENTS rules, repo-local skills, and explicit user instructions must override upstream Superpowers habits such as TDD-only execution, worktree creation, or branch cleanup. This keeps the repo deterministic and prevents process overhead the user did not request.

Alternative considered:
- Let upstream skill instructions execute in full whenever present. Rejected because they can conflict with repo-specific validation, approval, and documentation rules.

## Risks / Trade-offs

- [More workflow text can increase perceived process overhead] -> Keep the skip list explicit and allow low-risk non-trivial changes to use OpenSpec as the working plan without a separate approval pause.
- [Fallback `docs/superpowers/**` paths could still be overused] -> Restrict them to cases where no active OpenSpec change exists or OpenSpec is not required, and keep OpenSpec canonical whenever present.
- [Bilingual OpenSpec maintenance adds document work] -> Accept because the repo already treats paired English and Chinese workflow docs as a standing contract.

## Migration Plan

- Update `AGENTS.md` and `AGENTS.zh_CN.md` in the same change.
- Start using `chg-YYYYMMDD-HHMMSS-<slug>` names for new active OpenSpec changes.
- Do not rename archived or previously accepted change directories.

## Open Questions

- None.
