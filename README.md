# TableCV

TableCV turns OCR text boxes into a `pandas.DataFrame`. Use it when you already have OCR output from an image and want a simple table-like result without writing row and column grouping logic yourself.

OCR means optical character recognition: software reads text from an image. Most OCR tools return each piece of text with a bounding box, which is the rectangle around that text. TableCV uses those rectangles to estimate which text belongs in each row and column.

## Why Use It

- Works with any OCR tool that can return text boxes.
- Returns a familiar `pandas.DataFrame`.
- Keeps the core table extraction separate from heavy OCR engines.
- Supports an optional PaddleOCR path for users who want OCR and table extraction in one call.

## Installation

For table extraction from OCR results:

```bash
pip install tablecv
```

For the optional PaddleOCR helper:

```bash
pip install "tablecv[paddle]"
```

On Linux, PaddlePaddle may also need the system OpenMP runtime. For Ubuntu or Debian-based systems, install `libgomp1` if importing Paddle fails with a `libgomp.so.1` error.

## Requirements

- Python 3.13+
- `pandas` and `shapely` for the core extraction path
- PaddleOCR only if you call `extract_table()`

## Quick Start With Existing OCR Results

Use `extract_table_from_ocr()` when your OCR tool has already read the image.

```python
from tablecv import extract_table_from_ocr

ocr_results = [
    ((0, 0, 10, 5), "Name"),
    ((20, 0, 10, 5), "Qty"),
    ((0, 20, 10, 5), "Tea"),
    ((20, 20, 10, 5), "2"),
    ((0, 40, 10, 5), "Coffee"),
    ((20, 40, 10, 5), "1"),
]

df = extract_table_from_ocr(ocr_results)
print(df)
```

The OCR result format is:

```python
((x, y, width, height), text)
```

Here, `x` and `y` are the top-left position of the text box. `width` and `height` are the size of that box.

## Quick Start With PaddleOCR

Install the optional extra first:

```bash
pip install "tablecv[paddle]"
```

Then call `extract_table()` with an image path:

```python
from tablecv import extract_table

df = extract_table("invoice.png")
print(df)
```

`extract_table()` initializes PaddleOCR lazily. Importing `tablecv` does not download OCR models or require PaddleOCR unless you call this function.

## How It Works

TableCV estimates a table in four broad steps:

1. It groups OCR boxes that share similar vertical positions into rows.
1. It finds the strongest table-like region, ignoring surrounding document text such as invoice headers, addresses, and footers.
1. It chooses a reference row from repeated column patterns or the table header.
1. It maps each OCR box in the table region to the closest column.

This works best for documents where the table text boxes line up in repeated rows and columns. For example, it can extract a line-item table from an invoice page that also contains logos, billing details, totals, and footer text.

## Limitations

TableCV is a lightweight table estimator, not a full document understanding system.

- It does not detect table borders or merged cells.
- It returns the strongest table-like region, not every table on a page.
- It expects OCR boxes to be close to reading order and reasonably aligned.
- Skewed, rotated, handwritten, or heavily nested tables may need preprocessing.
- Real OCR accuracy depends on the OCR engine, image quality, language, and font.

## Troubleshooting

### `libgomp.so.1` Missing

PaddlePaddle depends on an OpenMP runtime on Linux. If `extract_table()` fails while importing Paddle with `libgomp.so.1: cannot open shared object file`, install the system package:

```bash
sudo apt-get update
sudo apt-get install libgomp1
```

You do not need PaddleOCR or `libgomp1` for `extract_table_from_ocr()`.

## Development

This project uses `uv`, Ruff, pytest, Bandit, and PyPI Trusted Publishing.

```bash
make sync
make test
make coverage
make check-commit
make build
```

Default tests use synthetic OCR boxes and do not download OCR models. Tests that require PaddleOCR, image files, model downloads, or external binaries should be marked as `integration`.

## Publishing

Pushes to `main` run the package quality gate and publish to PyPI with Trusted Publishing. Before this works, configure PyPI to trust:

- owner: `inquilabee`
- repository: `TableCV`
- workflow: `.github/workflows/python-publish.yml`
- environment: `pypi`
