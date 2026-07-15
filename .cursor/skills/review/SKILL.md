---
name: review
description: Review TableCV changes for package quality, public API compatibility, OCR behavior, tests, and release risk. Use when the user asks for a review or before publishing.
disable-model-invocation: true
---

# Review TableCV

Review all changes on the current branch or in the requested diff.

## Context

1. Read `AGENTS.md` and `.cursor/rules/`.
2. Inspect `git status --short`, branch, and diff.
3. Identify whether changes affect:
   - Public imports or function names.
   - OCR engine setup or optional dependencies.
   - Bounding-box row and column estimation.
   - Packaging metadata or release workflows.
   - Default vs integration tests.

## Gates

Run or verify:

```bash
make check-commit
make build
```

For real OCR/image behavior, also run:

```bash
make integration
```

## Review Focus

- Public API compatibility and migration notes.
- Lazy optional dependency behavior for PaddleOCR.
- Deterministic tests for default suite.
- Clear integration markers for image/OCR-engine checks.
- No secrets, publishing tokens, or skipped hooks.
- Version, metadata, and README consistency.

## Output

Lead with findings ordered by severity. Include file references, evidence, and whether each item blocks release. If no issues are found, say so and list any skipped gates or environment limits.
