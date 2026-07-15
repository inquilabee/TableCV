from collections import Counter, defaultdict, deque

import pandas as pd

from tablecv.types import OCRResult
from tablecv.utils.bounding_box import get_rows_from_boxes


def row_data_to_dataframe(
    rows: list[list[tuple[int, tuple[float, float, float, float]]]],
    ocr_results: list[OCRResult],
    row_count: int,
    col_count: int,
) -> pd.DataFrame:
    ocr_text_by_box = defaultdict(deque)
    for box, text in ocr_results:
        ocr_text_by_box[box].append(text)

    row_box_counts = Counter(cell_box for row in rows for _, cell_box in row)
    text_data = [[[] for _ in range(col_count)] for _ in range(row_count)]

    for idx, row in enumerate(rows):
        for cell_num, cell_box in row:
            if cell_num >= col_count:
                continue
            texts = ocr_text_by_box[cell_box]
            if row_box_counts[cell_box] == 1:
                text_data[idx][cell_num].extend(texts)
                texts.clear()
            elif texts:
                text_data[idx][cell_num].append(texts.popleft())

    data = [[None for _ in range(col_count)] for _ in range(row_count)]

    for row_idx, _row in enumerate(text_data):
        for col_idx, _cell in enumerate(_row):
            text = " ".join(text_data[row_idx][col_idx])
            data[row_idx][col_idx] = text or ""

    return pd.DataFrame(data)


def extract_table_from_ocr(ocr_results: list[OCRResult]) -> pd.DataFrame:
    boxes = [res[0] for res in ocr_results]
    if not boxes:
        return pd.DataFrame()

    row_count, col_count, rows = get_rows_from_boxes(boxes)
    if row_count == 0 or col_count == 0:
        return pd.DataFrame()

    return row_data_to_dataframe(rows, ocr_results, row_count, col_count)
