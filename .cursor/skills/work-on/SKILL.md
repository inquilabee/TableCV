---
name: work-on
description: End-to-end TableCV workflow. Use when starting or continuing package work, refactors, fixes, quality tasks, or release preparation.
disable-model-invocation: true
---

# Work On TableCV

Use this workflow for non-trivial changes.

## 1. Explore

1. Read `AGENTS.md` and applicable `.cursor/rules/`.
2. Check `git status --short`.
3. Read the relevant modules and tests before editing.
4. Identify whether the change affects public API, OCR behavior, tests, packaging, or release flow.

## 2. Plan

Create a short plan with:
- Files to touch.
- Public API compatibility impact.
- Tests to add or update.
- Verification commands.

Do not implement multi-file changes until the user has agreed when the task is ambiguous.

## 3. Implement

1. For bug fixes, write a regression test first and confirm it fails.
2. Make the smallest change that satisfies the plan.
3. Keep default tests deterministic; mark OCR-engine or image checks as `integration`.
4. Do not add a dependency until `pyproject.toml` has been checked for an existing tool.

## 4. Verify

Run the smallest relevant checks during work, then finish with:

```bash
make check-commit
make build
```

Use `make integration` only when the change needs real OCR/image proof.

## 5. Close Out

Summarize changed behavior, commands run, skipped checks, and any release notes. Do not commit, push, or publish unless the user explicitly asks.
