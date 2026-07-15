# Agents and Maintainers

This repository publishes `tablecv`, a Python package for turning OCR text boxes into table-shaped `pandas.DataFrame` objects.

## Start Here

- Rules: `.cursor/rules/`
- Skills: `.cursor/skills/`
- Package metadata and tool config: `pyproject.toml`
- Default tests: `tests/`

## Project Boundaries

- `tablecv/extract_table.py`: user-facing PaddleOCR wrapper and `extract_table()` API.
- `tablecv/utils/table_extraction.py`: converts OCR results into `DataFrame` output.
- `tablecv/utils/bounding_box.py`: estimates rows and columns from OCR bounding boxes.
- `tablecv/types.py`: shared public type aliases for OCR results and bounding boxes.

Preserve public imports from `tablecv/__init__.py` unless a breaking release is intentional and documented.

## Commands

```bash
make sync
make test
make coverage
make check-commit
make lint
make build
```

Default tests must not download OCR models, call external services, or require local image files. Tests that need PaddleOCR, image fixtures, or external binaries belong under `@pytest.mark.integration`.

## Package Workflow

This project uses `uv` and PEP 621 metadata.

- Add runtime dependencies in `[project].dependencies`.
- Add development tools in `[dependency-groups].dev`.
- Regenerate `uv.lock` after dependency changes.
- Build with `uv build`.
- Publish from GitHub Actions with `uv publish` and PyPI Trusted Publishing.

PyPI must be configured to trust the repository, workflow, and `pypi` environment before publishing from `main` works.

## Agent Rules

- Read `.cursor/rules/` before substantial edits.
- Plan before multi-file changes or public API changes.
- For bug fixes, write a regression test before production changes.
- Do not commit, push, open PRs, publish, or merge unless explicitly asked.
- Never bypass hooks with `--no-verify` or `SKIP=...`.
- Verify with fresh command output before claiming work is complete.
