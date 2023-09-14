# TableCV

Extract table from an image.

# Usage

There are two ways to get table from an image.

## Approach 1 (uses PaddleOCR)

Call `extract_table` (returns pandas Dataframe object).

```python
from tablecv import extract_table

print(extract_table(image_path=""))
```

## Approach 2

Perform ocr using your favourite OCR tool (EasyOCR, KerasOCR, PaddleOCR, WhateverOCR ...).

`ocr_results` object should look like the following:

```python
# list of tuple of bounding box and text

ocr_results = [
    (
        (1, 2, 3, 4), "a"   # (x, y, w, h), text
    ),
    (
        (4, 5, 6, 7), "b"
    ),
    ...
]
```

and then call `extract_table_from_ocr` method.

```python
from tablecv import extract_table_from_ocr

ocr_results: list[tuple[tuple[float, float, float, float], str]] = ...
print(extract_table_from_ocr(ocr_results))
```
