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
- Empty OCR results return an empty `DataFrame`.
- Duplicate text boxes preserve text order within a cell.
- Zero-width boxes do not crash overlap calculation.

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

1. Add unit tests for uneven rows and missing cells.
1. Add tests for noisy OCR boxes that should be filtered from the table.
1. Increase coverage threshold after the above tests land.
