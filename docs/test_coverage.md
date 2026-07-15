# Test Coverage

## Strategy

The default test suite must be deterministic. Tests under `tests/` use synthetic OCR boxes plus committed image fixtures with injected OCR engines. Integration tests are excluded from the default run. Default tests are selected by:

```bash
make test
```

Real OCR-engine checks belong in integration tests and should be marked with `@pytest.mark.integration`. Run them only when PaddleOCR, model downloads, image assets, and local binaries are part of the acceptance criteria:

```bash
make integration
```

## Covered in the Default Suite

- `extract_table_from_ocr()` builds a `DataFrame` from synthetic OCR boxes.
- `extract_table()` accepts real PNG and JPG image paths when an OCR engine is injected.
- Downloaded Magnific JPG fixtures are present and validated as real JPEG files.
- Downloaded Kirana invoice fixtures are present, attributed, and validated as real PNG files.
- Empty OCR results return an empty `DataFrame`.
- Duplicate text boxes preserve text order within a cell.
- Zero-width boxes do not crash overlap calculation.
- Full-document OCR with invoice-style headers and footers extracts the table region instead of collapsing into one column.
- Table headers can define the column grid when body rows have missing cells.
- Single-box noise inside a table band does not split one table into multiple outputs.
- Multi-cell metadata before a table header is excluded from the extracted table.

## Integration Coverage

The suite includes a PaddleOCR test against `tests/fixtures/images/simple_table.png`. It is not skipped when `make integration` is run; missing PaddleOCR, missing model downloads, or missing system libraries should fail the integration gate.

```bash
make integration
```

On Linux, PaddlePaddle may require `libgomp1`:

```bash
sudo apt-get update
sudo apt-get install -y libgomp1
```

## Next Priorities

1. Add deterministic coverage for documents with more than one real table.
1. Add targeted tests for skewed or rotated synthetic boxes if the core layout starts supporting them.
1. Increase coverage threshold after the above tests land.
