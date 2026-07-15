# Test Coverage

## Strategy

The default test suite must be deterministic. Tests under `tests/` use synthetic OCR boxes and are selected by:

```bash
make test
```

OCR-engine and image-fixture checks belong in integration tests and should be marked with `@pytest.mark.integration`. Run them only when PaddleOCR, model downloads, image assets, and local binaries are part of the acceptance criteria:

```bash
make integration
```

## Covered in the Default Suite

- `extract_table_from_ocr()` builds a `DataFrame` from synthetic OCR boxes.
- Empty OCR results return an empty `DataFrame`.
- Duplicate text boxes preserve text order within a cell.
- Zero-width boxes do not crash overlap calculation.

## Next Priorities

1. Add image-fixture integration tests for `extract_table()` with PaddleOCR.
1. Add unit tests for uneven rows and missing cells.
1. Add tests for noisy OCR boxes that should be filtered from the table.
1. Increase coverage threshold after the above tests land.
