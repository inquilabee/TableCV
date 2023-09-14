# TableCV

**TableCV** is a Python package designed to extract tables from images. It offers two approaches for extracting tables, allowing you to choose the one that best suits your needs.

## Installation

You can easily install **TableCV** using pip:

```bash
pip install tablecv
```

## Usage

### Approach 1 (using PaddleOCR)

**TableCV** offers a straightforward method to extract tables using PaddleOCR. This approach returns a pandas DataFrame object:

```python
from tablecv import extract_table

# Replace "image_path" with the path to your image
print(extract_table(image_path="your_image.png"))
```

### Approach 2 (OCR with Your Preferred Tool)

If you prefer using a different OCR tool like EasyOCR, KerasOCR, or any other OCR solution, you can still use **TableCV**. First, perform OCR on your image using your chosen tool. The OCR results should be structured as a list of tuples, each containing a bounding box and corresponding text:

```python
# List of tuples: (bounding box as (x, y, w, h), text)
ocr_results = [
    ((1, 2, 3, 4), "a"),
    ((4, 5, 6, 7), "b"),
    # Add more tuples as needed
]
```

After obtaining your OCR results, you can extract tables from them using **TableCV**:

```python
from tablecv import extract_table_from_ocr

# Replace "ocr_results" with your OCR results list
print(extract_table_from_ocr(ocr_results))
```

With these two approaches, **TableCV** provides flexibility for table extraction from images, whether you prefer using PaddleOCR or another OCR tool of your choice.
